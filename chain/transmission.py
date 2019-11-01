import time

from py3 import to_str, to_bytes


class Transmission(object):

    BROADCAST = -1      # dest -> BROADCAST

    def __init__(self, source_index, dest_index, payload):
        t = time.time()
        self.TID = "%d.%d.%d" % (source_index, int(t), int((t-int(t))*1000000))
        self.Src = source_index
        self.Dst = dest_index
        self.Payload = payload
        
    def to_bytes(self):
        return b"%s:%d:%d:%s" % (to_bytes(self.TID), self.Src, self.Dst, 
                to_bytes(self.Payload))

    @staticmethod        
    def from_bytes(buf):
        tid, src, dst, payload = buf.split(":", 3)
        tid = to_str(tid)
        src = int(src)
        dst = int(dst)
        t = Transmission(src, dst, payload)
        t.TID = tid
        return t
