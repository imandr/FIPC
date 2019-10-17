from py3 import to_str, to_bytes
import uuid

class CPacket:

    @staticmethod
    def from_bytes(msg):
        t, body = msg.split(b':', 1)
        if t == CPusher.Type:
                return CPusher.from_bytes(body)
        elif t == CToken.Type:
                return CToken.from_bytes(body)
        elif t == CMessage.Type:
                return CMessage.from_bytes(body)
        else:
            raise ValueError("Unknown CPacket type : '%s'" % (to_str(t),))
                        
    def to_bytes(self, body):
        return b"%s:%s" % (self.Type, body)

class   CMessage(CPacket):
    Type = b'M'
    Poll = -2
    Broadcast = -1

    def __init__(self, src = None, dst = None, body = '', mid = None):
        self.Src = src
        self.Dst = dst
        self.Body = body
        self.Type = CMessage.Type
        self.MID = to_bytes(mid or uuid.uuid4().hex)
        
    def __str__(self):
        return "[Message %s bcst:%s poll:%s %s->%s: %s]" % (self.MID, self.isBroadcast(),
                self.isPoll(), self.Src, self.Dst, self.Body)

    @staticmethod
    def from_bytes(msg):
        mid, src, dst, body = msg.split(b":", 3)
        return CMessage(int(src), int(dst), body, mid)
        
    def to_bytes(self):
        return CPacket.to_bytes(self, 
            b'%s:%d:%d:%s' % (self.MID, self.Src, self.Dst, to_bytes(self.Body)))

    def isBroadcast(self):
        return self.Dst == CMessage.Broadcast

    def isPoll(self):
        return self.Dst == CMessage.Poll

class CPusher(CPacket):
    Type = b'P'
    def __init__(self, src = None, seq = None):
        self.Type = CPusher.Type
        self.Src = src
        self.Seq = seq

    @staticmethod
    def from_bytes(msg):
        #print 'Pusher::decode(%s)' % msg
        src, dst = msg.split(b':')
        return CPusher(int(src), int(dst))

    def to_bytes(self):
        return CPacket.to_bytes(self, 
            b'%d:%d' % (self.Src, self.Seq))

class CToken(CPacket):
    Type = b'T'
    def __init__(self, dst = None):
        self.Type = CToken.Type
        self.Dst = dst

    @staticmethod
    def from_bytes(msg):
        #print 'Pusher::decode(%s)' % msg
        return CToken(int(msg))

    def to_bytes(self):
        return CPacket.to_bytes(self, 
            b'%d' % (self.Dst,))


    
