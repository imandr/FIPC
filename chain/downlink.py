from pythreader import PyThread, Primitive, synchronized
from SockStream import SockStream
from socket import *
import random

from py3 import to_str, to_bytes

class DownLink(PyThread):

    def __init__(self, node, ip, edge_port, diagonal_port):
        PyThread.__init__(self)
        self.Node = node
        self.Index = node.Index
        self.ListenSock = None
        self.DownStream = None
        self.DownIndex = None

    def run(self):
    
        self.ListenSock = socket(AF_INET, SOCK_STREAM)
        self.ListenSock.setcockopt(SOL_SOCKET, SO_REUSE_ADDR, 1)
        self.ListenSock.bind((ip, edge_port))
        self.ListenSock.listen(1)
        
        diagonal_sock = socket(AF_INET, SOCK_DGRAM)
        diagonal_sock.setcockopt(SOL_SOCKET, SO_REUSE_ADDR, 1)
        diagonal_sock.bind((ip, diagonal_port))
        
        while True:
            lsn_fd = self.ListenSock.fileno()
            diag_fd = diagonal_sock.fileno()
            lst = [lsn_fd, diag_fd]
            down_fd = None
            if self.DownStream is not None:
                down_fd = self.DownStream.fileno()
                lst.append(down_fd)
            r, w, e = select.select(lst, [], lst, 10.0)
            if lsn_fd in r:
                self.acceptDownConnection(self.ListenSock)
            if diag_fd in r:
                self.receiveDiagonalTransmission(diagonal_sock)
            if down_fd in r or down_fd in e:
                self.receiveEdgeTransmission()
                
    def acceptDownConnection(self, lsn_sock):
        try:    sock, addr = lsn_sock.accept()
        except: return
        
        stream = SockStream(sock)
        msg = stream.recv(tmo = 1.0)
        if msg.startswith("HELLO "):
            cmd, inx = msg.split(" ")
            inx = int(inx)
            if self.DownIndex is None or self.closerDown(inx, self.DownIndex):
                # accept new down connection
                if self.DownStream is not None:
                    self.DownStream.close()
                self.DownStream = stream
                stream.send("OK")
            else:
                stream.close()
                
    def receiveDiagonalTransmission(self, dsock):
        try:    data, addr = dsock.recvfrom(65000)
        except: pass
        if data:
            # check source sock address here - later - FIXME
            t = Transmission.from_bytes(data)
            self.Node.processTransmission(t, diagonal=True)
    
    def receiveEdgeTransmission(self):
        self.DownStream.readMore(1024*1024, 10.0)
        if self.DownStream.msgReady():
            msg = self.DownStream.getMsg()
            t = Transmission.from_bytes(msg)
            self.Node.processTransmission(t, diagonal=False)
        elif self.DownStream.EOF:
            self.DownStream.close()
            self.DownStream = None
