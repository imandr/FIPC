#
# @(#) $Id: Systat.py,v 1.4 2000/05/18 18:19:39 ivm Exp $
#
# $Log: Systat.py,v $
# Revision 1.4  2000/05/18 18:19:39  ivm
# Fixed memory leak in Systat.py
#
#
# Revision 1.16  1999/05/26 16:16:25  ivm
# Added method sessionRoots() and pids() to Systat,
# Changed farmd communication timeout to 3 seconds in JobStat
#
# Revision 1.15  1999/04/29 21:14:19  ivm
# Fixed for IRIX64 where ppid(1) = 1
#
# Revision 1.14  1999/04/28 19:25:26  ivm
# Updated for IRIX64
#
# Revision 1.12  1999/03/15 17:37:09  ivm
# *** empty log message ***
#
# Revision 1.11  1999/03/15 17:33:40  ivm
# Minor clean-up
#
# Revision 1.10  1999/03/15 16:53:04  ivm
# Added pgid, sid, uid and gid
# Use uname()
#
# Revision 1.9  1999/03/05 22:03:36  ivm
# Fixed syntax error
#
# Revision 1.8  1999/03/05 21:13:30  ivm
# Added OS = 'OSF1','osf1'
#
# Revision 1.7  1999/03/04 20:27:11  ivm
# Use psmodule
#
# Revision 1.6  1999/01/05 21:49:20  ivm
# Added implementation for IRIX (using ps -e -o...)
#
#
import glob
import string
import os
import sys

_PSModule = None
try:
	import ps
	_PSModule = ps
except:
	pass
	
class ProcSysInfo:
	def __init__(self, ppid = 0, cpu = 0):
		self.ppid = ppid
		self.cpu = cpu
		self.acpu = cpu
		self.Children = []
		self.uid = 0
		self.gid = 0
		self.pgid = 0
		self.sid = 0
		
def _update_linux():
	procs = {}
	dirs = glob.glob('/proc/[0-9]*')
	for dir in dirs:
		file = dir + '/stat' 
		try:	
			stt = os.stat(file)
			uid = stt[4]
			gid = stt[5]
		except: continue
		try:	f = open(file, 'r')
		except:	continue
		if not f:	continue
		line = f.readline()
		f.close()
		if not line:	continue
		items = string.split(line)
		if len(items) < 17:	continue
		try:
			pid = string.atoi(items[0])
			ppid = string.atoi(items[3])
			pgid = string.atoi(items[4])
			sid = string.atoi(items[5])
			utime = string.atoi(items[13])/100
			stime = string.atoi(items[14])/100
			cutime = string.atoi(items[15])/100
			cstime = string.atoi(items[16])/100
		except:	continue
		p = ProcSysInfo(ppid, utime + stime + cutime + cstime)
		p.sid = sid
		p.pgid = pgid
		p.uid = uid
		p.gid = gid
		p.cmd = ['(unknown)']
		file = dir + '/cmdline'
		try:	f = open(file, 'r')
		except:
			pass
		else:
			l = f.readline()
			if l:
				p.cmd = string.splitfields(l,'\0')
		procs[pid] = p
	return procs

def _update_irix():
	procs = {}
	if _PSModule == None:	return
	pids = glob.glob('/proc/pinfo/[0-9][0-9]*')
	#print pids
	for pid in pids:
		inx = string.rindex(pid,'/')
		pid = string.atoi(pid[inx+1:])
		#print pid
		try:	psi = _PSModule.ps(pid)
		except: 
			#print 'Error in ps(%d):' % pid, \
			#	(sys.exc_type, sys.exc_value)
			continue
		p = ProcSysInfo(psi.PPid, psi.Time + psi.CTime)
		p.cmd = string.split(psi.Cmd)[1:]
		p.gid = psi.Gid
		p.uid = psi.Uid
		p.pgid = psi.PGid
		p.sid = psi.Sid
		#print 'Inserting pid=%d, cpu=%d, acpu=%d, cmd=%s' % \
		#		(pid, psi.Time, psi.CTime, p.cmd)
		procs[pid] = p
	return procs
		
def _update_null(self):
	return {}

class Systat:
	def __init__(self, osn=None):
		self.Procs = {}
		#print 'Systat: OS = %s' % os
		if osn == None:
			osn = os.uname()[0]
		osn = string.upper(osn)
		if osn[:4] == 'IRIX':
			osn = 'IRIX'
		try:
			self._update = { 
				'LINUX' : _update_linux,
				'IRIX64' : _update_irix,
				'IRIX' : _update_irix,
				'OSF1' : _update_irix,
				'SUNOS' : _update_irix,
				'SOLARIS' : _update_irix
			} [osn]
		except KeyError:
			self._update = _update_null
			
	def update(self):
		self.Procs = self._update()
		for pid, p in self.Procs.items():
			ppid = p.ppid
			if ppid != 0:
				try:	pp = self.Procs[ppid]
				except KeyError:
					p.ppid = 0
					continue
				pp.Children.append(pid)
				while ppid != 0:
					pp = self.Procs[ppid]
					pp.acpu = pp.acpu + p.cpu
					if pp.ppid != ppid:
						ppid = pp.ppid
					else:
						ppid = 0

	def killTree(self, rootpid, signo):
		try:	os.kill(rootpid, signo)
		except:	pass
		try:			p = self[rootpid]
		except KeyError: 	return
		for pid in p.Children:
			self.killTree(pid, signo)
		
	def killSession(self, sid, signo):
		for pid, p in self.Procs.items():
			if p.sid == sid:
				try:	os.kill(pid, signo)
				except: pass

	def killGroup(self, pgid, signo):
		for pid, p in self.Procs.items():
			if p.pgid == pgid:
				try:	os.kill(pid, signo)
				except: pass

	def pids(self):
		return self.Procs.keys()

	def has_key(self, pid):
		return self.Procs.has_key()

	def sessionRoots(self, sessId):
		lst = []
		for pid, pi in self.Procs.items():
			if pi.sid != sessId:	continue
			ppid = pi.ppid
			if ppid == 0 or ppid == pid or (not self.Procs.has_key(ppid)) or \
					self.Procs[ppid].sid != sessId:
				lst.append(pid)
		return lst
		
	def __getitem__(self, pid):
		return self.Procs[pid]

	def __len__(self):
		return len(self.Procs)
	
if __name__ == '__main__':
	import sys
	pid = string.atoi(sys.argv[1])
	s = Systat()
	s.update()
	if s:
		p = s[pid]
		print p.ppid, p.cpu, p.acpu, p.cmd, p.Children
