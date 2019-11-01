from pythreader import PyThread, Primitive, synchronized
from SockStream import SockStream
from socket import *
import random, select

from py3 import to_str, to_bytes

class UpLink(PyThread):

    def __init__(self, node, nodes, ndiagonals):
        PyThread.__init__(self)
        self.Node = node
        self.Index = node.Index
        # nodes: [(ip, edge_port, diagonal_port)] indexed by the node index
        nodes = [(inx, ip, edge_port, diagonal_port) 
                for inx, (ip, edge_port, diagonal_port) in enumerate(nodes)
        ]
        self.UpNodes = (nodes[inx:] + nodes[:inx])[::-1]  # sorted in upwards order
        self.DiagonalNodes = []
        self.NDiagonals = ndiagonals
        self.UpStream = None
        self.UpIndex = None

    def connectStream(self, ip, port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(1.0)
        try:    
            sock.connect((ip, port))
        except:
            sock.close()
            return None
        stream = SockStream(sock)
        reply = stream.sendAndRecv("HELLO %d" % (self.Index,))
        if reply != "OK":
            return None
        sock.settimeout(None)
        return stream

    @synchronized
    def connectUp(self):
        while self.UpStream is None:
            for j, (inx, ip, port, _) in enumerate(self.UpNodes):
                stream = self.connectStream(ip, port)
                if stream is not None:  
                    self.UpStream = stream
                    self.UpInx = inx
                    self.DiagonalNodes = self.UpNodes[j+1:]
                    break
            else:
                self.sleep(1.0)

    def run(self):
        self.DiagonalSock = socket(AF_INET, SOCK_DGRAM)
        self.UpStream = self.connectUp()

        while True:
        
            if self.UpStream is None:
                self.connectUp()

            while self.UpStream is not None:
                self.UpStream.zing()
                self.UpStream.readMore(1024, 10.0)
                while self.UpStream.msgReady():
                    self.UpStream.getMsg()     # upstream should never send anything
                                                # except zing/zong thing or disconnection
                if self.UpStream.eof():
                    self.UpStream.close()
                    self.Node.closeDownLink()
                    self.UpStream = None
                else:
                    self.UpStream.readMore(1024, 10.0)

    @synchronized
    def send(self, transmission, diagonal_only=False):

        tbytes = transmission.to_bytes()
        
        ndiagonals = min(self.NDiagonals, len(self.DiagonalNodes))
        if ndiagonals:
            diagonals = random.sample(self.DiagonalNodes, ndiagonals)
            for inx, ip, _, port in diagonals:
                self.DiagonalSock.sendto(tbytes, (ip, port))
        
        if not diagonal_only:
            sent = False
            while not sent:
            
                if self.UpStream is None:
                    self.connectUp()

                if self.UpStream is None:
                    raise RingError("Can not connect upstream socket")

                nsent = self.UpStream.send(tbytes)
                if nsent < len(tbytes):
                    self.UpStream.Sock.close()
                    self.UpStream = None
                    self.sleep(1.0)
                else:
                    sent = True
                
        
        
            
            
            
        
           
