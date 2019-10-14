from TCPServer import *
from SockStream import *
from chain import *
from chainpkt import *
from socket import *
import Parser
import string
import time
import select
import regex

class	TermIO:
	def __init__(self, locksrv):
		self.LockSrv = locksrv
	
	def doRead(self, fd, sel):
		if fd != 0: return
		l = sys.stdin.readline()
		l = string.strip(l)
		lst = string.split(l)
		if len(lst) >= 1:
			if lst[0] == 'C':
				self.LockSrv.createString(self, lst[1])
			elif lst[0] == 'MS':
				self.LockSrv.matchAndSet(self, 
						lst[1], lst[2], lst[3])
			elif lst[0] == 'D':
				self.LockSrv.deleteVar(self, lst[1])
			elif lst[0] == '#':
				self.LockSrv.ping(self, lst[1])

	def done(self, rid, sts, msg, ret):
		print 'Done:', rid, sts, msg, ret

class	SockSrv(TCPServer):
	def __init__(self, map, sel, locksrv):
		bound = 0
		for host, port in map:
			try:	TCPServer.__init__(self, port, sel)
			except: pass
			else:
				bound = 1
				break
		if not bound:
			raise 'Can not bind'
		self.LockSrv = locksrv

	def createClientInterface(self, sock, peer, sel):
		print 'Client connection from ', peer
		if self.LockSrv.readyForClients():
			return SockIO(sock, self.LockSrv, sel)
		else:
			return None
		
class	SockIO:
	def __init__(self, sock, locksrv, sel):
		self.LockSrv = locksrv
		self.Sock = sock
		self.Str = SockStream(sock, '\n')
		self.Sel = sel
		self.Sel.register(self, rd = self.Sock.fileno())
		self.Requests = {}
		self.Uid = None
		self.Gid = None
			
	def doRead(self, fd, sel):
		if fd != self.Sock.fileno():	return
		if self.Str.readMore(1000):
			msg = self.Str.getMsg()
			msg = string.strip(msg)
			lst = list(eval(msg))
			print 'Received from client: %s' % lst
			if self.Uid == None:
				# accept only HELLO
				if lst[0] != 'HELLO' or len(lst) != 3:
					self.disconnect()
				self.Uid = lst[1]
				self.Gid = lst[2]
				self.Str.send('OK')
				print 'Received HELLO from uid/gid = %s/%s' % \
						(self.Uid, self.Gid)
			else:
				self.sendRequest(lst)
		elif self.Str.eof():
			self.disconnect()

	def sendRequest(self, lst):
		#print 'sendRequest(%s)' % lst
		if len(lst) >= 1:
			rid = self.LockSrv.newReqId()
			self.Requests[rid] = lst
			if lst[0] == 'C':
				if len(lst) >= 4:	val = lst[3]
				else:				val = ''
				self.LockSrv.createString(self, rid, lst[1], lst[2], val)
			elif lst[0] == 'MS':
				#print lst
				self.LockSrv.matchAndSet(self, rid,
						lst[1], lst[2], lst[3], lst[4])
			elif lst[0] == 'DEL':
				self.LockSrv.deleteString(self, rid, lst[1])
			elif lst[0] == 'G':
				self.LockSrv.getValue(self, rid, lst[1])
			elif lst[0] == 'I':
				self.LockSrv.getInfo(self, rid, lst[1])
			elif lst[0] == '#':
				self.LockSrv.ping(self, rid, string.join(lst[1:]))
			elif lst[0] == 'V':
				self.done(rid, 1, 'OK', (LockSrv.Version, ChainLink.Version))
			elif lst[0] == 'DUMP':
				if len(lst) > 1:
					self.LockSrv.dumpVars(self, rid, lst[1])
				else:
					self.LockSrv.dumpVars(self, rid)
					
	def done(self, rid, sts, reason, val):
		try:	del self.Requests[rid]
		except: pass
		tup = (sts, reason, val)
		self.Str.send(repr(tup))
		self.disconnect()
		
	def disconnect(self):
		self.Sel.unregister(rd = self.Sock.fileno())
		self.Sock.close()

	def retry(self, rid):
		try:	lst = self.Requests[rid]
		except KeyError:
			return
		del self.Requests[rid]
		self.sendRequest(lst)

class	Request:
	def __init__(self, rid, cl, cmd_args):
		self.Id = rid
		self.Client = cl
		self.CmdArgs = cmd_args

	def retry(self):
		self.Client.retry(self.Id)
		
	def done(self, sts, reason, val):
		self.Client.done(self.Id, sts, reason, val)

class	Variable:
	RightMap = {		# flag -> list of actions
		'-': '',	'r':'r',	'x':'rwd'}
		
	def __init__(self, uid=None, gid=None, prot=None, value = ''):
		self.Uid = uid
		self.Gid = gid
		self.Prot = prot		# string 'gw' where g and w are in '-rx'
		self.Value = value

	def get(self):
		return self.Value
		
	def set(self, x):
		self.Value = x
		
	def dump(self):
		t = (self.Uid, self.Gid, self.Prot, self.Value)
		return repr(t)
	
	def restore(self, txt):
		self.Uid, self.Gid, self.Prot, self.Value = eval(txt)

	def checkPerm(self, op, uid, gid):
		if uid == self.Uid: return 1	# full access to owner
		gp, wp = tuple(self.Prot)
		if gid == self.Gid: 	prot = gp
		else:					prot = wp
		return op in self.RightMap[prot]
		
class	VarStorage:
	def __init__(self):
		self.Dict = {}

	def __setitem__(self, name, var):
		self.Dict[name] = var
		
	def __getitem__(self, name):
		return self.Dict[name]

	def __delitem__(self, name):
		del self.Dict[name]

	def has_key(self, name):
		return self.Dict.has_key(name)
		
	def keys(self, name):
		return self.Dict.keys()

	def items(self):
		return self.Dict.items()

	def dump(self):
		d = {}
		for n, v in self.Dict.items():
			d[n] = v.dump()
		return d
	
	def restore(self, d):
		self.Dict = {}
		for n, t in d.items():
			v = Variable()
			v.restore(t)
			self.Dict[n] = v
			
class	LockSrv(ChainSegment):

	Version = "$Id: fipc-srv.py,v 1.8 1999/10/12 16:15:08 ivm Exp $"

	def __init__(self, inx, map, sel):
		ChainSegment.__init__(self, inx, map, sel)
		self.PendingRequests = {}
		self.SentRequests = {}
		self.Vars = VarStorage()
		self.State = 'NeedSync'
		self.NextRId = 1
		self.Dispatch = {
			'DELS':  	self.doDeleteStrMsg,
			'CRES': 	self.doCreateStrMsg,
			'PING': 	self.doPingMsg,
			'MSET': 	self.doMatchSetMsg,
			'SET':		self.doSetMsg
			# the following are handled in a different way
			#'SQ':		self.doSyncReqMsg,
			#'SR':		self.doSyncRepMsg
			}
			
		self.ExecSendDispatch = {
			'CRES': 	self.execCreateStringRequest,
			'DELS': 	self.execDeleteStringRequest,
			'MSET': 	self.execMatchAndSetRequest,
			'PING': 	self.execPingRequest
		}
		self.LastSQSent = 0
		self.LastPusherSent = 0
		self.PusherTimeOut = 1
		self.SQTimeOut = 1
		self.sendSyncRequest()

	def readyForClients(self):
		return self.State == 'GotSync'
		
	def newReqId(self):
		rid = self.NextRId
		self.NextRId = self.NextRId + 1
		return rid

	def suspendRequest(self, rid, cl, *cmd):
		# defer request until we receive token
		print 'suspendRequest #%s: cmd = ' % rid, cmd
		self.PendingRequests[rid] = Request(rid, cl, cmd)
		if self.haveToken():
			#print 'We have the token -- forward it'
			self.forwardToken()
		self.sendPusher()
					
	def run(self, tmo):
		ChainSegment.run(self, tmo)
		self.idle()

	def processMessageCbk(self, src, dst, msg):
		print 'Message from %s, to %s: <%s>' % (src, dst, msg)
		if dst == CMessage.Broadcast:
			#print 'BCST: ', org, msg
			self.procBcst(src, dst, msg)
		elif dst == CMessage.Poll:
			#print 'POLL: ', org, msg
			msg = self.procPoll(src, dst, msg)
			#print 'poll-> ', msg
			if msg != None:
				self.sendMessage(src, dst, msg)
		else:
			if dst == self.Inx or org == self.Inx:
				self.procDirect(org, dst, msg)

	def unpackMsg(self, txt):
		tup = eval(txt)
		if type(tup) == type([]):	tup = tuple(tup)
		if type(tup) != type(()):	tup = (tup)
		#print 'unpackMsg(%s) -> ' % txt, tup
		return tup
		
	def packMsg(self, cmd, *args):
		#print 'packMsg(%s, %s) -> ' % (cmd, args),
		if type(cmd) == type(()):
			tup = cmd
		else:
			tup = [cmd]
			for x in args:
				tup.append(x)
			tup = tuple(tup)
		#print '%s' % (tuple(tup),)
		return repr(tup)
		
	def procBcst(self, src, dst, msg):
		if self.State != 'NeedSync':
			self.processMessage(src, dst, msg)

	def procDirect(self, src, dst, msg):
		if self.State != 'NeedSync':
			self.processMessage(src, dst, msg)

	def procPoll(self, src, dst, msg):	# returns packed message to forward
		# Poll can be only SQ or SR message
		tup = self.unpackMsg(msg)
		if len(tup) < 1:	return msg
		cmd = tup[0]
		args = tup[1:]
		#print 'procPoll: cmd = %s, args = ' % cmd, args
		if cmd == 'PING':
			if src == self.Inx:
				self.processMessage(src, dst, msg)
				msg = None
			else:
				#print args
				rid = args[0]
				str = args[1]
				lst = args[2]
				lst.append('%d@%s' % (self.Inx, gethostname()))
				msg = self.packMsg('PING', rid, str, lst)
		else:
			if self.State == 'NeedSync':
				if cmd == 'SR':
					self.doSyncRepMsg(src, args)
					if src == self.Inx:
						msg = None
				elif cmd == 'SQ' and src == self.Inx:
					self.State = 'GotSync'
					msg = None
			else:	# have sync
				if src == self.Inx: 
					msg = None
				elif cmd == 'SQ':
					dump = self.doSyncReqMsg(src, args)
					msg = self.packMsg('SR',dump)
		return msg
		
	def processMessage(self, src, dst, msg):
		# Never gets called in NeedSync state
		#print 'processMessage(%s, %s, %s)' % (src, dst, msg)
		lst = self.unpackMsg(msg)
		if len(lst) >= 1:
			cmd = lst[0]
			rqid = lst[1]
			args = lst[2:]
			if self.Dispatch.has_key(cmd):
				sts, reason, ret = self.Dispatch[cmd](src, dst, args)

				if src == self.Inx and self.SentRequests.has_key(rqid):
					r = self.SentRequests[rqid]
					r.done(sts, reason, ret)
					del self.SentRequests[rqid]

	def doSetMsg(self, src, dst, args):
		# SET rqid name value
		name, val = args
		if self.Vars.has_key(name):
			old = self.Vars[name].get()
			self.Vars[name].set(val)
			print 'SET <%s>: <%s> -> <%s>' % (name, old, val)
			return 1, 'OK', old
		else:
			return 0, 'Not found', ''
		
	def doCreateStrMsg(self, src, dst, args):
		# CRES rqid name uid gid prot value
		#print 'doCreateStrMsg(%s, %s, %s)' % (src, dst, args)
		name, uid, gid, prot, val = args
		if self.Vars.has_key(name):
			sts = 0
			msg = 'Already exists'
			ret = self.Vars[name].get()
			if not self.Vars[name].checkPerm('r', uid, gid):
				ret = '???'
		else:
			self.Vars[name] = Variable(uid, gid, prot, val)
			sts = 1
			msg = 'OK'
			ret = ''
		return sts, msg, ret
			
	def doPingMsg(self, src, dst, args):
		#print 'doPingMsg: args = ', args
		str = args[0]
		lst = args[1]
		lst.append('%d@%s' % (self.Inx, gethostname()))
		return 1, 'OK', (str, lst)

	def substitute(self, re, old, new):
		out = ''
		while new:
			#print 'Old: <%s> new: <%s> out: <%s>' % (old, new, out)
			inx = string.find(new, '%')
			if inx < 0:
				out = out + new
				new = ''
			elif inx == len(new)-1:
				out = out + '%'
				new = ''
			else:	# inx > len(new)-1
				out = out + new[:inx]
				n = new[inx+1]
				new = new[inx+2:]
				if n in '0123456789':
					n = string.atoi(n)
				else:
					continue
				#print 're[%d] = <%s>' % (n, re.regs[n])
				try:	
					i, j = re.regs[n]
					out = out + old[i:j]
				except: pass
		return out					

	def matchSubst(self, old, ptrn, ptrn1, val):
		new = None
		if not ptrn1 or not regex.match(ptrn1, old) == len(old):
			re = regex.compile(ptrn)
			#print 'Matching str=<%s> to prtn=<%s>' % (old, ptrn)
			if re.match(old) == len(old):
				new = self.substitute(re, old, val)
		return new
		
	def doMatchSetMsg(self, src, dst, args):
		# ('MSET',rqid, name, pattern, value)
		# val can contain %n, which will be replaced with contents
		# of n-th RE register. %% is interpreted as '%'
		name, ptrn, ptrn1, val = args
		#print 'doMatchSetMsg(%s)' % (args,)
		if self.Vars.has_key(name):
			old = self.Vars[name].get()
			new = self.matchSubst(old, ptrn, ptrn1, val)
			if new != None:
				self.Vars[name].set(new)
				sts = 1
				msg = 'OK'
				ret = old
			else:
				sts = 0
				msg = 'Mismatch'
				ret = old
			print 'LockSrv: %s: old=<%s>, new=<%s>' % \
				(name, old, self.Vars[name].get())
		else:
			sts = 0
			msg = 'Not found'
			ret = ''
		return sts, msg, ret

	def doDeleteStrMsg(self, src, dst, args):
		# ('DELS',rqid,name)
		name = args[0]

		if self.Vars.has_key(name):
			del self.Vars[name]
			sts = 1
			msg = 'OK'
			ret = ''
		else:
			sts = 0
			msg = 'Not found'
			ret = ''		
		return sts, msg, ret

	def doSyncReqMsg(self, src, args):
		# never called in NeedSync state
		# see procPoll()
		return self.Vars.dump()

	def doSyncRepMsg(self, src, args):
		self.Vars.restore(args[0])
		self.State = 'GotSync'	

	def sendSyncRequest(self, sendNow = 0):
		if sendNow or time.time() > self.LastSQSent + self.SQTimeOut:
			msg = self.packMsg('SQ')
			self.sendMessage(self.Inx, CMessage.Poll, msg)
			self.LastSQSent = time.time()

	def sendPusher(self, sendNow = 0):
		if sendNow or time.time() > self.LastPusherSent + self.PusherTimeOut:
			ChainSegment.sendPusher(self)
			self.LastPusherSent = time.time()

	def sendMsg(self, src, dst, msg, sendNow = 0):
		if sendNow:
			self.sendMessage(src, dst, msg)
		else:
			self.MessagesToSend.append((src, dst, msg))
			
	def getOutMsgList(self):
		lst = self.MessagesToSend
		self.MessagesToSend = []
		return lst

	def gotTokenCbk(self):
		#print 'gotTokenCbk: state = %s' % self.State
		self.LastPusherSent = 0 # so that next sendPusher() will send it
		if self.State == 'NeedSync':
			self.sendSyncRequest(sendNow = 1)
		else:
			self.flushRequests()
			
	def flushRequests(self):
		# We received a token (or already had one)
		# Now is the time to throw away all sent, but unconfirmed
		# requests, then send all pending requests.
		#print 'Flushing requests...'
		#print 'Pending: ', self.PendingRequests
		#print 'Sent:    ', self.SentRequests

		if len(self.SentRequests) > 0 or len(self.PendingRequests) > 0:
			newSent = {}

			#
			# Send at most one pending request if needed
			for rid, r in self.PendingRequests.items():
				del self.PendingRequests[rid]
				if self.execAndSend(r):
					self.forwardToken(self.Inx)
					newSent[rid] = r
					break

			#
			# reject all sent requests. Sometimes, retry() re-inserts
			# the request into PendingRequests
			for rid, r in self.SentRequests.items():
				r.retry()

			self.SentRequests = newSent
			
		#print 'Done with flushing.'
		#print 'Pending: ', self.PendingRequests
		#print 'Sent:    ', self.SentRequests

	def idle(self):
		if self.State == 'NeedSync':
			self.sendSyncRequest()

		if not self.haveToken() and (len(self.SentRequests) > 0 or
					len(self.PendingRequests) > 0):
			self.sendPusher()

	#
	# Cliend command execution at token time
	#
	def execAndSend(self, r):
		cmd_args = r.CmdArgs
		cmd = cmd_args[0]
		args = cmd_args[1:]
		print 'execAndSend: cmd = <%s>, args=<%s>' % (cmd, args)
		return self.ExecSendDispatch[cmd](r, r.Client, args)

	def execPingRequest(self, r, cl, args):
		self.sendMessage(self.Inx, CMessage.Poll,
			self.packMsg('PING', r.Id, args[0], args[1]))
		return 1
		
	def execCreateStringRequest(self, r, cl, args):
		name = args[0]
		prot = args[1]
		val = args[2]
		if self.Vars.has_key(name):
			val = '???'
			var = self.Vars[name]
			if var.checkPerm('r', cl.Uid, cl.Gid):
				val = var.get()
			r.done(0, 'Already exists', val)
			return 0
		self.sendMessage(self.Inx, CMessage.Broadcast, 
				self.packMsg('CRES', r.Id, name, cl.Uid, cl.Gid, prot, val))
		return 1

	def execDeleteStringRequest(self, r, cl, args):
		name = args[0]
		if not self.Vars.has_key(name):
			r.done(0, 'Not found', '')
			return 0
		if not self.Vars[name].checkPerm('d', cl.Uid, cl.Gid):
			r.done(0, 'Protection violation', '')
			return 0
		self.sendMessage(self.Inx, CMessage.Broadcast,
				self.packMsg('DELS', r.Id, name))
		return 1

	def execMatchAndSetRequest(self, r, cl, args):
		name = args[0]
		ptrn = args[1]
		ptrn1 = args[2]
		val = args[3]
		
		try:	var = self.Vars[name]
		except KeyError:
			r.done(0, 'Not found', '')
			return 0
		if not var.checkPerm('w', cl.Uid, cl.Gid):
			r.done(0, 'Protection violation', '')
			return 0
		old = var.get()
		new = self.matchSubst(old, ptrn, ptrn1, val)
		if new == None:
			r.done(0, 'Mismatch', old)
			return 0
		self.sendMessage(self.Inx, CMessage.Broadcast, 
				self.packMsg('SET', r.Id, name, new))
		return 1
					
	#
	# Client interface
	#
	def createString(self, cl, rid, name, prot, val = ''):
		print 'Request #%s: Create String <%s> = <%s> (%d/%d,%s)' % (
			rid, name, val, cl.Uid, cl.Gid, prot)
		if self.Vars.has_key(name):
			print 'request failed'
			val = '???'
			var = self.Vars[name]
			if var.checkPerm('r', cl.Uid, cl.Gid):
				val = var.get()
			cl.done(rid, 0, 'Already exists', val)
		else:
			self.suspendRequest(rid, cl, 'CRES', name, prot, val)
			print 'request suspended'

	def deleteString(self, cl, rid, name):
		print 'Request #%s: Delete String <%s>' % (
			rid, name)
		if not self.Vars.has_key(name):
			print 'request failed'
			cl.done(rid, 0, 'Not found', '')
		else:
			v = self.Vars[name]
			if not v.checkPerm('d', cl.Uid, cl.Gid):
				cl.done(rid, 0, 'Protection violation', '')
			else:
				self.suspendRequest(rid, cl, 'DELS', name)
				print 'request suspended'
		
	def ping(self, cl, rid, str = ''):
		print 'Request #%s: Ping <%s>' % (rid, str)
		self.suspendRequest(rid, cl, 'PING', str, [])

	def matchAndSet(self, cl, rid, name, ptrn, ptrn1, val):
		print 'Request #%s: Match-Set <%s> <%s>/<%s> -> <%s>' % (
			rid, name, ptrn, ptrn1, val)
		if not self.Vars.has_key(name):
			print 'request failed'
			cl.done(rid, 0, 'Not found', '')
		else:
			v = self.Vars[name]
			if not v.checkPerm('w', cl.Uid, cl.Gid):
				cl.done(rid, 0, 'Protection violation', '')
			else:
				self.suspendRequest(rid, cl, 'MSET', name, ptrn, ptrn1, val)
				print 'request suspended'
				
	def getValue(self, cl, rid, name):
		if self.Vars.has_key(name):
			v = self.Vars[name]
			if not v.checkPerm('r', cl.Uid, cl.Gid):
				cl.done(rid, 0, 'Protection violation', '')
			else:
				cl.done(rid, 1, 'OK', v.get())
		else:
			cl.done(rid, 0, 'Not found', '')

	def getInfo(self, cl, rid, name):
		if self.Vars.has_key(name):
			v = self.Vars[name]
			#if not v.checkPerm('r', cl.Uid, cl.Gid):
			#	cl.done(rid, 0, 'Protection violation', '')
			cl.done(rid, 1, 'OK', (v.Uid, v.Gid, v.Prot))
		else:
			cl.done(rid, 0, 'Not found', (None, None, None))
			

	def dumpVars(self, cl, rid, pattern = '.*'):
		dict = {}
		re = regex.compile(pattern)
		for name, var in self.Vars.items():
			if re.match(name) > 0 and var.checkPerm('r', cl.Uid, cl.Gid):
				dict[name] = (var.get(), var.Uid, var.Gid, var.Prot)
		#print 'dumpVars: dict=%s' % dict
		#print '          Dict=%s' % self.Vars
		#print '          pattern=<%s>' % pattern
		cl.done(rid, 1, 'OK', dict)

if __name__ == '__main__':
	import getopt
	from fipc_map import FIPCMap

	usage = 'fipc-srv [-m FIPC-map-file] [-i server-index]'
	
	def myGetOpt(lst, optStr):
		dict = {}
		opts, args = getopt.getopt(lst, optStr)
		for opt, optv in opts:
			try:	optv = string.atoi(optv)
			except: pass
			dict[opt] = optv
		return dict, args

	optDict, optArgs = myGetOpt(sys.argv[1:], 'm:i:')
	if not optDict.has_key('-m'):
		if os.environ.has_key('FIPC_MAP_FILE'):
			optDict['-m'] = os.environ['FIPC_MAP_FILE']
		else:
			print 'Use -m option or environment variable FIPC_MAP_FILE '
			print 'to specify FIPC map file.'
			print usage
			os.exit(2)

	map = FIPCMap(optDict['-m'])
	if not optDict.has_key('-i'):
		optDict['-i'] = -1
	inx = optDict['-i']
	if type(inx) != type(0):
		print 'Server index (-i) must be an integer'
		print usage
		os.exit(2)
	sel = Selector()
	ls = LockSrv(optDict['-i'], map.chainMap(), sel)
	ssrv = SockSrv(map.serverMap(), sel, ls)

	while 1:
		ls.run(10)
			
