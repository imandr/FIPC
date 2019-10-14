from py3 import to_str, to_bytes

class   CMessage:
    Type = b'M'
    Poll = -2
    Broadcast = -1

    def __init__(self, src = None, dst = None, body = ''):
        self.Src = src
        self.Dst = dst
        self.Body = body
        self.Type = CMessage.Type

    @staticmethod
    def from_bytes(msg):
        src, dst, body = msg.split(b":", 2)
        return CMessage(int(src), int(dst), body)
        
    def to_bytes(self):
        return b'%d:%d:%s' % (self.Src, self.Dst, self.Body)

    def isBroadcast(self):
        return self.Dst == CMessage.Broadcast

    def isPoll(self):
        return self.Dst == CMessage.Poll

class CPusher:
    Type = b'P'
    def __init__(self, src = None, seq = None):
        self.Type = CPusher.Type
        self.Src = src
        self.Seq = seq

    @staticmethod
    def from_bytes(self, msg):
        #print 'Pusher::decode(%s)' % msg
        src, dst = msg.split(':')
        return CPusher(src, dst)

    def to_bytes(self):
        return b'%d:%d' % (self.Src, self.Seq)

class CToken:
    Type = b'T'
    def __init__(self, dst = None):
        self.Type = CToken.Type
        self.Dst = dst

    @staticmethod
    def from_bytes(self, msg):
        #print 'Pusher::decode(%s)' % msg
        return CToken(int(msg))

    def to_bytes(self):
        return b'%d' % self.Dst


class CPacket:
    def __init__(self, body = None):
        self.Body = body

    @staticmethod
    def from_bytes(self, msg):
        t, body = msg.split(b':', 1)
        if t == CPusher.Type:
                self.Body = CPusher.from_bytes(body)
        elif t == CToken.Type:
                self.Body = CToken.from_bytes(body)
        elif t == CMessage.Type:
                self.Body = CMessage.from_bytes(body)
                        
    def to_bytes(self):
        #print 'Pkt::encode(): body = %s' % self.Body
        return b'%s:%s' % (self.Body.Type, self.Body.to_bytes())
