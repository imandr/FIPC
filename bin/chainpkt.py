#
# @(#) $Id: chainpkt.py,v 1.2 1999/08/19 21:25:02 ivm Exp $
#
# $Log: chainpkt.py,v $
# Revision 1.2  1999/08/19 21:25:02  ivm
# Implemented delete command, fixed bug in 'ls'
# New format of messages, use regexp
#
# Revision 1.1  1999/07/12 19:35:52  ivm
# *** empty log message ***
#
# Revision 1.5  1999/05/21 14:22:36  ivm
# Latest version with mixed ChainLink
#
# Revision 1.4  1999/05/20  19:22:15  ivm
# *** empty log message ***
#
# Revision 1.4  1999/05/20  19:22:15  ivm
# *** empty log message ***
#
#

import string
import regex

class	CMessage:
	Type = 'M'
	Poll = -2
	Broadcast = -1

	def __init__(self, src = None, dst = None, body = ''):
		self.Src = src
		self.Dst = dst
		self.Body = body
		self.Type = CMessage.Type
		
	def decode(self, msg):
		#print 'Request: decoding "%s"' % msg,
		re = regex.compile('\(-?[0-9]+\):\(-?[0-9]+\):\(.*\)')
		re.match(msg)
		self.Src = string.atoi(re.group(1))
		self.Dst = string.atoi(re.group(2))
		self.Body = re.group(3)
		#print ' ---> "%s"' % self.Body
		
	def encode(self):
		txt = '%d:%d:%s' % (self.Src, self.Dst, self.Body)
		#print 'CMessage.encode() -> ', txt
		return txt

	def isBroadcast(self):
		return self.Dst == CMessage.Broadcast

	def isPoll(self):
		return self.Dst == CMessage.Poll

class CPusher:
	Type = 'P'
	def __init__(self, src = None, seq = None):
		self.Type = CPusher.Type
		self.Src = src
		self.Seq = seq

	def decode(self, msg):
		#print 'Pusher::decode(%s)' % msg
		re = regex.compile('\(-?[0-9]+\):\(-?[0-9]+\)')
		re.match(msg)
		self.Src = string.atoi(re.group(1))
		self.Seq = string.atoi(re.group(2))

	def encode(self):
		return '%d:%d' % (self.Src, self.Seq)

class CToken:
	Type = 'T'
	def __init__(self, dst = None):
		self.Type = CToken.Type
		self.Dst = dst

	def decode(self, msg):
		#print 'Pusher::decode(%s)' % msg
		self.Dst = string.atoi(msg)

	def encode(self):
		return '%d' % self.Dst


class CPacket:
	def __init__(self, body = None):
		self.Body = body

	def decode(self, msg):
		re = regex.compile('\([A-Za-z][A-Za-z0-9]*\):\(.*\)')
		re.match(msg)
		t, body = re.group(1,2)
		if t == CPusher.Type:
			self.Body = CPusher()
			self.Body.decode(body)
		elif t == CToken.Type:
			self.Body = CToken()
			self.Body.decode(body)
		elif t == CMessage.Type:
			self.Body = CMessage()
			self.Body.decode(body)
				
	def encode(self):
		#print 'Pkt::encode(): body = %s' % self.Body
		txt = '%s:%s' % (self.Body.Type, self.Body.encode())
		return txt
