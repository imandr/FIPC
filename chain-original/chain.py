#
# @(#) $Id: chain.py,v 1.6 2001/09/28 17:06:17 ivm Exp $
#
# $Log: chain.py,v $
# Revision 1.6  2001/09/28 17:06:17  ivm
# Made it work with Python 2.1
#
# Revision 1.5  2001/05/07 11:28:30  ivm
# Fixed for new FCSLIB
#
# Revision 1.4  1999/10/12 16:15:07  ivm
# Fixed bug in chain with multiple tokens
#
# Revision 1.3  1999/08/17 21:55:54  ivm
# Made UPS compliant
# Use single config file
#
# Revision 1.2  1999/08/03 19:47:23  ivm
# Make connection timeout in chain 5 seconds
# Use connect with timeout in client
#
# Revision 1.1  1999/07/12 19:35:52  ivm
# *** empty log message ***
#
# Revision 1.11  1999/06/01 19:27:44  ivm
# Pinging implemented
#
# Revision 1.10  1999/05/28  15:49:20  ivm
# Use time-out in connect()
#
# Revision 1.9  1999/05/21  18:14:06  ivm
# Fixed simultaneous SET problem
#
# Revision 1.6  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.6  1999/05/20  15:03:32  ivm
# Version with deferred execution (correct one)
#
# Revision 1.4  1999/05/18  14:37:08  ivm
# Implemented versions command
#
# Revision 1.4  1999/05/18  14:37:08  ivm
# Implemented versions command
#
# Revision 1.2  1999/05/17  18:14:03  ivm
# Debug messages cleaned up
#
# Revision 1.4  1999/04/19  19:25:55  ivm
# Recovery implemented
#
# Revision 1.4  1999/04/19  19:25:55  ivm
# Recovery implemented
#
#

import string
import sys
import os
from chainpkt import *
from SockStream import SockStream
from Selector import *
from socket import *
import select
import errno
import time

Error = 'FIPC Error'

class	ChainSegment:
	def __init__(self, inx, map, sel):
		self.UpSock = None
		self.UpStr = None
		self.DnSock = None
		self.DnStr = None
		self.Sel = sel
		self.Map = map
		self.UpInx = None
		self.DnInx = None
		self.Inx = self.initServerSock(inx, map)
		if self.Inx < 0:
			# some error
			raise Error, 'Can not allocate Chain port'
		self.Sel.register(self, rd = self.SSock.fileno())
		self.Token = None
		self.PusherSeq = None
		self.IgnorePusher = -1
		self.LastPushSeq = 0
		self.connect()
		self.LastPing = 0
		
	def initServerSock(self, inx, map):
		if inx >= 0:
			h, port = self.Map[inx]
			self.SSock = socket(AF_INET, SOCK_STREAM)
			self.SSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			self.SSock.bind((h, port))
			self.SSock.listen(2)
			return inx
		else:	# pick first available
			last_exc_type = None
			last_exc_value = None
			for inx in range(len(map)):
				h, p = map[inx]
				sock = socket(AF_INET, SOCK_STREAM)
				sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
				try:	sock.bind((h,p))
				except:
					last_exc_type = sys.exc_type
					last_exc_value = sys.exc_value
				else:
					sock.listen(2)
					self.SSock = sock
					return inx
			# all attempts failed...
			if last_exc_type != None:
				raise last_exc_type, last_exc_value
			return -1
			
	def isCloserUp(self, i, j):		# i is closer than j
		if i > self.Inx:	i = i - len(self.Map)
		if j > self.Inx:	j = j - len(self.Map)
		return i > j

	def isCloserDown(self, i, j):	# i is closer than j
		return self.isCloserUp(j, i)
		
	def upIndex(self):
		return self.UpInx

	def downIndex(self):
		return self.DnInx
				
	def connectSocket(self, addr, tmo = -1):
		# returns either connected socket or None on timeout
		# -1 means infinite
		s = socket(AF_INET, SOCK_STREAM)
		if tmo < 0:
			s.connect(addr)
			return s

		s.setblocking(0)
		if s.connect_ex(addr) == 0:
			s.setblocking(1)
			return s
		#print 'selecting...'	
		r,w,x = select.select([], [s], [], tmo)
		if s.connect_ex(addr) == 0:
			s.setblocking(1)
			return s
		try:	s.getpeername()
		except:
			print sys.exc_type, sys.exc_value
			s.close()
			return None
		s.setblocking(1)
		return s
												
	def connect(self):
		inx = self.Inx
		#print 'Connect: my inx = ', self.Inx
		for i in range(len(self.Map)):
			inx = inx - 1
			if inx < 0: 	inx = len(self.Map) - 1
			# sock = socket(AF_INET, SOCK_STREAM)
			# try to connect to server #inx
			addr = self.Map[inx]
			sock = None
			print 'connecting to #', inx, ' at ', addr
			try:
				sock = self.connectSocket(addr, 5)
			except:
				print sys.exc_type, sys.exc_value
				pass
			if sock == None:
				print 'Connection failed'
				continue				
			str = SockStream(sock, '\n')
			print 'Sending HELLO...'
			str.send('HELLO %d' % self.Inx)
			print 'Up connection to %d established' % inx
			self.UpSock = sock
			self.Sel.register(self, rd = self.UpSock.fileno())
			self.UpStr = str
			self.UpInx = inx
			return inx
		return -1
					
	def doRead(self, fd, sel):
		#print 'doRead(fd=%d)' % fd
		#os.system('netstat | grep 7001')
		if fd == self.SSock.fileno():
			#print 'doRead(server, fd = %d)' % fd
			self.doConnectionRequest()
		elif self.DnSock != None and fd == self.DnSock.fileno():
			#print 'doRead(down, fd = %d)' % fd
			self.doReadDn()
		elif self.UpSock != None and fd == self.UpSock.fileno():
			#msg = self.UpSock.recv(1000)
			#print 'doRead(up, fd = %d) : <%s>' % (fd, msg)
			self.doReadUp()
		#print 'doRead(): Sel: %s' % sel.ReadList
		
	def getHello(self, str):
		msg = str.recv(1000)
		lst = string.split(msg)
		inx = -1
		print 'Hello msg: <%s>' % msg
		if len(lst) >= 2 and lst[0] == 'HELLO':
			try:			inx = string.atoi(lst[1])
			except: 		pass
		return inx
						
	def doConnectionRequest(self):
		refuse = 0
		s, addr = self.SSock.accept()
		#print 'Connection request from %s, sock = %s' % (addr, s)
		ip, port = addr
		str = SockStream(s, '\n')
		inx = self.getHello(str)
		if inx < 0: refuse = 1	# Unknown client. Refuse
		if not refuse and self.DnSock != None and self.DnInx != self.Inx:
			 # check if this client is "closer" than our down connection
			refuse = not self.isCloserDown(inx, self.DnInx)

		if self.UpSock == None and not refuse:
			# if so far we were alone, it means that this is good
			# time to try to connect
			#print 'trying to connect...'
			refuse = (self.connect() < 0)

		#print 'refuse = ', refuse
		if refuse:
			s.close()
		else:
			# this client is "closer". Close old connection and 
			# keep this new client
			if self.DnSock != None:
				#print 'New client is closer. Disconnect'
				self.Sel.unregister(rd = self.DnSock.fileno())
				self.DnSock.close()
			self.DnSock = s
			self.DnInx = inx
			self.DnStr = SockStream(self.DnSock, '\n')
			self.Sel.register(self, rd = s.fileno())
			self.downConnectedCbk(inx)
			print 'Down connection to %d established' % inx

	def downConnectedCbk(self, inx):	#virtual
		pass
		
	def doReadDn(self):
		self.DnStr.readMore(1024)
		#print 'DnStr: EOF = %s, Buf = <%s>' % (self.DnStr.EOF, 
		#		self.DnStr.Buf)
		while self.DnStr.msgReady():
			msg = self.DnStr.getMsg()
			print 'RCVD DN:<%s>' % msg[:100]
			pkt = CPacket()
			pkt.decode(msg)
			pkt = pkt.Body
			if pkt.Type == CToken.Type:
				self.gotToken(pkt)
			elif pkt.Type == CPusher.Type:
				self.gotPusher(pkt)
			elif pkt.Type == CMessage.Type:
				self.gotMessage(pkt)
		if self.DnStr.eof():
			# Down link is broken. Close the socket,unregister it
			self.downDisconnectedCbk()
			self.closeDnLink()

	def doReadUp(self): 	# nothing meaningfull, just pings
		self.UpStr.readMore(1024)
		while self.UpStr.msgReady():
			self.UpStr.getMsg()
		if self.UpStr.eof():
			# Down link is broken. Close the socket,unregister it
			self.upDisconnectedCbk()
			self.closeUpLink()
			self.connect()

	def downDisconnectedCbk(self):		#virtual
		pass
		
	def gotMessage(self, msg):
		#print 'gotMessage(%s)' % msg.Body
		if msg.isBroadcast() or msg.isPoll() or msg.Dst == self.Inx:
			self.processMessageCbk(msg.Src, msg.Dst, msg.Body) 	# pure virtual
		if msg.Src != self.Inx:
			forward = 1
			if msg.isPoll():
				forward = 0
			elif msg.isBroadcast():
				forward = not self.isCloserUp(msg.Src, self.UpInx)
			else:
				forward = not self.isCloserUp(msg.Dst, self.UpInx)
			if forward:
				self.sendUp(msg)

	def gotPusher(self, pusher):
		#print 'Got pusher(src=%s, seq=%s)' % (pusher.Src, pusher.Seq)
		src = pusher.Src
		if src == self.Inx:
			#print 'self.Token=', self.Token, ' PusherSeq = ', self.PusherSeq
			if not self.haveToken() and \
					self.PusherSeq != None and \
					pusher.Seq > self.IgnorePusher and \
					self.PusherSeq >= pusher.Seq:
				self.createToken()
		elif self.haveToken():
			if self.isCloserUp(self.Token.Dst, src):
				self.Token.Dst = src
			self.forwardToken()
		else:
			if self.PusherSeq != None and self.Inx > src:
				self.PusherSeq = None
			self.sendUp(pusher)

	def flushOutMsgs(self):
		lst = self.getOutMsgList()		# pure virtual
		#print 'flushOutMsgs: lst = ', lst
		for src, dst, txt in lst:
			self.sendMessage(src, dst, txt)
		return len(lst)

	def sendMessage(self, src, dst, txt):
		forward = 1
		msg = CMessage(src, dst, txt)
		if not msg.isBroadcast() and not msg.isPoll():
			forward = dst == self.Inx or not \
				self.isCloserUp(dst, self.UpInx)
		if forward:
			self.sendUp(msg)
	
	def gotToken(self, token):
		#print 'Got token'
		self.Token = token
		#
		# ignore all pushers we sent so far
		self.IgnorePusher = self.LastPushSeq
		self.PusherSeq = None
		# send our messages
		self.gotTokenCbk()
		if self.haveToken():
			# the callback above may have forwarded the token

			if token.Dst != self.Inx and self.isCloserUp(token.Dst, self.UpInx):	# the guy died
				token.Dst = self.Inx
			if token.Dst != self.Inx:
				self.forwardToken()
			
	def gotTokenCbk(self): 		# virtual
		#print 'Empty gotTokenCbk'
		pass				
					
	def upDisconnectedCbk(self):
		print 'up link broken'

	def needToken(self):
		#print 'Need token... ', self.Token
		#if self.WaitMode != 'n':
		#	return
		#print 'Need token... ', self.Token
		if self.haveToken():
			self.flushOutMsgs()
		else:
			self.sendPusher()
			#self.SendPusher = 1
						
	def createToken(self):
		print 'creating token...'
		self.PusherSeq = None
		self.Token = CToken(self.Inx)
		self.forwardToken()
		
	def forwardToken(self, to = None):
		if self.Token != None:
			if to != None:
				if self.Token.Dst != self.Inx and \
							self.isCloserUp(self.Token.Dst, to):
					self.Token.Dst = to
			self.sendUp(self.Token)
			self.Token = None
		

	def sendPusher(self):
		#print 'Sending pusher...'
		seq = self.LastPushSeq + 1
		self.LastPushSeq = seq
		self.PusherSeq = seq
		p = CPusher(self.Inx, seq)
		self.sendUp(p)

	def closeDnLink(self):
		if self.DnSock != None:		
			print 'closing down link'
			self.Sel.unregister(rd = self.DnSock.fileno())
			self.DnSock.close()
			self.DnSock = None
			self.DnStr = None

	def closeUpLink(self):
		if self.UpSock != None:		
			print 'closing up link'
			self.Sel.unregister(rd = self.UpSock.fileno())
			self.UpSock.close()
			self.UpSock = None
			self.UpStr = None

	def sendUp(self, msg):
		if self.UpSock == None:
			if self.connect() < 0:
				# something is wrong: we have down link, but
				# can not connect anywhere. Break down link
				# assume that down peer is dead
				self.closeDnLink()

		if self.UpStr != None:
			pkt = CPacket(msg)
			txt = pkt.encode()
			print 'SEND UP:<%s>' % txt[:100]
			self.UpStr.send(txt)
			#os.system('netstat | grep 7001')
			
	def run(self, tmo = -1):
		#print 'run(): Sel: %s' % self.Sel.ReadList
		#os.system('netstat | grep 7001')
		self.Sel.select(tmo)
		#print self.LastPing, time.time()
		if self.LastPing < time.time() - 300:	# ping every 5 minutes
			if self.UpSock != None:
				#print 'Pinging up...'
				self.UpStr.zing(1000)			# disconnect after 15 minutes
				#print 'UpStr: EOF = %s, Buf = <%s>, LastTxn = %s' % (
				#	self.UpStr.EOF, self.UpStr.Buf, self.UpStr.LastTxn)
			if self.DnSock != None:
				#print 'Pinging down...'
				self.DnStr.zing(1000)
			self.LastPing = time.time()
			
	def haveToken(self):
		#print 'haveToken: token = ', self.Token
		return self.Token != None

class	CallBackStub:
	def __init__(self, fcn, arg):
		self.Fcn = fcn
		self.Arg = arg

	def invoke(self):
		self.Fcn(self.Arg)

class ChainLink(ChainSegment):

	Version = "$Id: chain.py,v 1.6 2001/09/28 17:06:17 ivm Exp $"

	def __init__(self, inx, map, sel):
		ChainSegment.__init__(self, inx, map, sel)
		self.OutMsgList = []
		self.InMsgList = []
		
	def sendMsg(self, dst, msg, src = None, sendNow = 0):
		if src == None:
			src = self.Inx
		if sendNow:
			self.sendMessage(src, dst, msg)
		else:
			# buffer it
			self.OutMsgList.append((src, dst, msg))
			self.needToken()

	def insertMsg(self, dst, msg):
		self.OutMsgList = [(self.Inx, dst, msg)] + self.OutMsgList
		self.needToken()
	
	def processMessageCbk(self, src, dst, msg):
		self.InMsgList.append((src, dst, msg))
		
	def haveMsg(self):
		return len(self.InMsgList) > 0

	def getOutMsgList(self):
		lst = self.OutMsgList
		self.OutMsgList = []
		return lst
	
	def getMsg(self):
		if not self.haveMsg():
			return None
		m = self.InMsgList[0]
		self.InMsgList = self.InMsgList[1:]
		return m
		
	def recvMsg(self):
		while not self.haveMsg():
			self.run()
		return self.getMsg()

	def upDisconnectCbk(self):
		print 'up link broken'

	def waitForToken(self):	
		while not self.haveToken():
			self.needToken()
			self.run(10)
			
	def addCallback(self, name, fcn, arg = None):
		cb = CallBackStub(fcn, arg)
		#print 'adding callback self.%sCbk' % name
		exec('self.%sCbk = cb.invoke' % name)
		
