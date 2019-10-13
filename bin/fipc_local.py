#
# @(#) $Id: fipc_local.py,v 1.3 1999/09/28 21:40:18 ivm Exp $
#
# $Author: ivm $
#
# $Log: fipc_local.py,v $
# Revision 1.3  1999/09/28 21:40:18  ivm
# Added objects() and rmdir() methods to FIPCClient
#
# Revision 1.2  1999/08/18 17:07:03  ivm
# Added fipc_common.py
# Added END to fipc.table
#
# Revision 1.1  1999/07/12 19:35:54  ivm
# *** empty log message ***
#
# Revision 1.6  1999/06/14 20:17:25  ivm
# Implemented timed-out connect to the server
#
# Revision 1.5  1999/06/01 20:26:45  ivm
# *** empty log message ***
#
# Revision 1.4  1999/05/20  20:36:05  ivm
# Fixed recursive call
#
# Revision 1.4  1999/05/20  20:36:05  ivm
# Fixed recursive call
#
# Revision 1.3  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.3  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.2  1999/05/17  15:10:21  ivm
# *** empty log message ***
#
# Revision 1.2  1999/05/17  15:10:21  ivm
# *** empty log message ***
#
# Revision 1.1  1999/05/12  20:20:48  ivm
# Initial revision
#
# Revision 1.1  1999/05/12  20:20:48  ivm
# Initial revision
#
#

from TCPServer import *
from Selector import *
from SockStream import *
from socket import *
from Systat import *
import signal

class	IPSCLocal(TCPServer):
	def __init__(self, port, sel):
		TCPServer.__init__(self, port, sel)
	
	def createClientInterface(self, sock, peer, sel):
		return LocalClientIF(sock, sel)

class	LocalClientIF:
	def __init__(self, sock, sel):
		self.Sock = sock
		self.Str = SockStream(sock, '\n')
		sel.register(self, rd = sock.fileno())
		
	def doRead(self, fd, sel):
		if fd != self.Sock.fileno():	return
		self.Str.readMore(1000)
		while self.Str.msgReady():
			msg = self.Str.getMsg()
			lst = string.split(msg)
			if len(lst) < 1:	continue
			cmd = lst[0]
			ans = self.doCommand(cmd, lst[1:])
			if ans: self.Str.send(ans)
		if self.Str.eof():
			sel.unregister(rd = self.Sock.fileno())
			self.Sock.close()
			self.Str = None
	
	def doCommand(self, cmd, args):
		if cmd == 'SESS':
			if len(args) < 1:	return 'ERR Usage: SESS <sess-id>'
			cid = args[0]
			scope = 's'
			if cid[0] in ('p','s'):
				scope = cid[0]
				cid = cid[1:]
			try:	cid = string.atoi(cid)
			except: return 'ERR Usage: SESS <sess-id>'
			ss = Systat()
			ss.update()
			if scope == 's':
				for pid in ss.pids():
					pi = ss[pid]
					#print pid, pi.sid, pi.cmd
					if pi.sid == cid:	return '1'
			elif scope == 'p':
				if cid in ss.pids():	return '1'
			return '0'
			
if __name__ == '__main__':
	sel = Selector()
	loc = IPSCLocal(6001, sel)
	while 1:
		sel.select(1000)
