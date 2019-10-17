import sys, traceback
import os
from chainpkt import CMessage, CPusher, CToken, CPacket
from socket import *
import select
import errno
import time
from SockStream import SockStream
from py3 import to_str, to_bytes
from pythreader import PyThread, Primitive

class ChainException(Exception):
    def __init__(self, text=""):
        self.Text = text
        
    def __str__(self):
        return "ChainException: %s" % (text,)

def poll(dispatch, tmo):
    p = select.poll()
    
    map = {}
    channels = 
    for channel, function in dispatch:
        if channel is not None:
            fd = channel if isinstance(channel, int) else channel.fileno()
            map[fd] = (channel, function)
            p.register(fd, select.POLLIN)
    
    if len(map) > 0:
        fired = p.poll(tmo)
        for fd, mask in fired:
            channel, function = map[fd]
            function(channel)
    
class   ChainSegment(PyThread):
        def __init__(self, inx, map, sel):
                PyThread.__init__(self)
                self.UpSock = None
                self.UpStr = None
                self.DnSock = None
                self.DnStr = None
                self.Sel = sel
                self.Map = map
                self.UpInx = None
                self.DnInx = None
                self.Inx = self.initServerSock(inx, map)
                if self.Inx is None:
                        # some error
                        raise ChainException('Can not allocate Chain port')
                self.Sel.register(self, rd = self.SSock.fileno())
                self.Token = None
                self.PusherSeq = None
                self.IgnorePusher = -1
                self.LastPushSeq = 0
                self.LastPing = 0
                print ("ChainSegment: connected")

        def io(self, tmo = None):
            poll([
                    (self.SSock,        self.doConnectionRequest),
                    (self.DnSock,       self.doReadDn),
                    (self.UpSock,       self.doReadUp)
                ],
                tmo
            )
            
        def connect(self):
                #print 'Connect: my inx = ', self.Inx
                for i in range(len(self.Map)):
                        inx = self.Inx - i - 1
                        if inx < 0: inx += len(self.Map)
                        # sock = socket(AF_INET, SOCK_STREAM)
                        # try to connect to server #inx
                        addr = self.Map[inx]
                        sock = None
                        print('connecting to #', inx, ' at ', addr)
                        try:
                                sock = self.connectSocket(addr, 5)
                        except:
                                print((sys.exc_type, sys.exc_value))
                                pass
                        if sock == None:
                                print('Connection failed')
                                continue                                
                        stream = SockStream(sock)
                        print('Sending HELLO...')
                        stream.send(b'HELLO %d' % self.Inx)
                        print(('Up connection to %d established' % inx))
                        self.UpSock = sock
                        self.Sel.register(self, rd = self.UpSock.fileno())
                        self.UpStr = stream
                        self.UpInx = inx
                        
                        #
                        # wait for down connection
                        #
                        
                        while self.DnStr is None:
                            self.run(1)
                        
                        return inx
                else:
                    # this should connect at least to self
                    raise RuntimeError("Can not connect uspream")
                    
        def run(self):
            while True:
                self.connect()
                self.waitForDownConnection()
        
                while True:
                    poll([
                        (self.SSock,        self.doConnectionRequest),
                        (self.DnSock,       self.doReadDn),
                        (self.UpSock,       self.doReadUp)
                    ],
                    10
                )

        def doReadDn(self):
                self.DnStr.readMore(1024)
                #print 'DnStr: EOF = %s, Buf = <%s>' % (self.DnStr.EOF, 
                #               self.DnStr.Buf)
                while self.DnStr.msgReady():
                        msg = self.DnStr.getMsg()
                        print(('RCVD DN:<%s>' % msg[:100]))
                        pkt = CPacket.from_bytes(msg)
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

        def doReadUp(self):     # nothing meaningfull, just pings
                self.UpStr.readMore(1024)
                while self.UpStr.msgReady():
                        self.UpStr.getMsg()     # upstream should never send anything
                                                # except zing/zong thing or disconnection
                if self.UpStr.eof():
                        # Down link is broken. Close the socket,unregister it
                        print('up link broken')
                        self.closeUpLink()
                        self.connect()

                
        def initServerSock(self, inx, map):
                if inx is not None:
                        h, port = self.Map[inx]
                        self.SSock = socket(AF_INET, SOCK_STREAM)
                        self.SSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
                        self.SSock.bind((h, port))
                        self.SSock.listen(2)
                        return inx
                else:   # pick first available
                        last_exc = None
                        for inx, (h, p) in enumerate(map):
                                sock = socket(AF_INET, SOCK_STREAM)
                                sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
                                try:    sock.bind((h,p))
                                except Exception as e:
                                        last_exc = e
                                else:
                                        sock.listen(2)
                                        self.SSock = sock
                                        return inx
                        # all attempts failed...
                        if last_exc is not None:
                                raise last_exc
                        return None
                        
        def isCloserUp(self, i, j):             # i is closer than j
                if i > self.Inx:        i -= len(self.Map)
                if j > self.Inx:        j -= len(self.Map)
                return i > j

        def isCloserDown(self, i, j):   # i is closer than j
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
                print ("connectSocket(%s): not connected" % (addr,))
                try:    s.getpeername()
                except:
                        print((traceback.format_exc()))
                        s.close()
                        return None
                s.setblocking(1)
                return s
                                                                                                
        def connect(self):
                #print 'Connect: my inx = ', self.Inx
                for i in range(len(self.Map)):
                        inx = self.Inx - i - 1
                        if inx < 0: inx += len(self.Map)
                        # sock = socket(AF_INET, SOCK_STREAM)
                        # try to connect to server #inx
                        addr = self.Map[inx]
                        sock = None
                        print(('connecting to #', inx, ' at ', addr))
                        try:
                                sock = self.connectSocket(addr, 5)
                        except:
                                print((sys.exc_type, sys.exc_value))
                                pass
                        if sock == None:
                                print('Connection failed')
                                continue                                
                        stream = SockStream(sock)
                        print('Sending HELLO...')
                        stream.send(b'HELLO %d' % self.Inx)
                        print(('Up connection to %d established' % inx))
                        self.UpSock = sock
                        self.Sel.register(self, rd = self.UpSock.fileno())
                        self.UpStr = stream
                        self.UpInx = inx
                        
                        #
                        # wait for down connection
                        #
                        
                        while self.DnStr is None:
                            self.run(1)
                        
                        return inx
                else:
                    # this should connect at least to self
                    raise RuntimeError("Can not connect uspream")
                                        
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
                
        def getHello(self, s):
                msg = to_str(s.recv(1000))
                print(('Hello msg: <%s>' % msg))
                inx = None
                hello, inx_txt = msg.split()
                if hello == "HELLO":
                    inx = int(inx_txt)
                return inx
                                                
        def doConnectionRequest(self):
                refuse = False
                s, addr = self.SSock.accept()
                #print 'Connection request from %s, sock = %s' % (addr, s)
                ip, port = addr
                stream = SockStream(s)
                inx = self.getHello(stream)
                if inx is None: refuse = True  # Unknown client. Refuse
                if not refuse and self.DnSock != None and self.DnInx != self.Inx:
                         # check if this client is "closer" than our down connection
                        refuse = not self.isCloserDown(inx, self.DnInx)

                if self.UpSock == None and not refuse:
                        # if so far we were alone, it means that this is good
                        # time to try to connect
                        #print 'trying to connect...'
                        refuse = (self.connect() is None)

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
                        self.DnStr = SockStream(self.DnSock)
                        self.Sel.register(self, rd = s.fileno())
                        self.downConnectedCbk(inx)
                        print(('Down connection to %d established' % inx))

        def downConnectedCbk(self, inx):        #virtual
                pass
                
        def doReadDn(self):
                self.DnStr.readMore(1024)
                #print 'DnStr: EOF = %s, Buf = <%s>' % (self.DnStr.EOF, 
                #               self.DnStr.Buf)
                while self.DnStr.msgReady():
                        msg = self.DnStr.getMsg()
                        print(('RCVD DN:<%s>' % msg[:100]))
                        pkt = CPacket.from_bytes(msg)
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

        def doReadUp(self):     # nothing meaningfull, just pings
                self.UpStr.readMore(1024)
                while self.UpStr.msgReady():
                        self.UpStr.getMsg()     # upstream should never send anything
                                                # except zing/zong thing or disconnection
                if self.UpStr.eof():
                        # Down link is broken. Close the socket,unregister it
                        print('up link broken')
                        self.closeUpLink()
                        self.connect()

        def downDisconnectedCbk(self):          #virtual
                pass
                
        def gotMessage(self, msg):
                print ('gotMessage(%s)' % msg.Body)
                
                if msg.Src == self.Inx:
                    self.messageConfirmedCbk(msg)
                else:
                    self.messageReceivedCbk(msg)
                    forward = True
                    if msg.isPoll():
                            forward = False
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
                        # the callback above may have forwarded the token and we no longer have it
                        if token.Dst != self.Inx and self.isCloserUp(token.Dst, self.UpInx):    # the guy died
                                token.Dst = self.Inx
                        if token.Dst != self.Inx:
                                self.forwardToken()
                        
        def needToken(self):
                if not self.haveToken():
                        self.sendPusher()
                                                
        def createToken(self):
                print('creating token...')
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
                print("sendPusher: %s" % (p,))
                self.sendUp(p)

        def closeDnLink(self):
                if self.DnSock != None:         
                        print('closing down link')
                        self.Sel.unregister(rd = self.DnSock.fileno())
                        self.DnSock.close()
                        self.DnSock = None
                        self.DnStr = None

        def closeUpLink(self):
                if self.UpSock != None:         
                        print('closing up link')
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
                        txt = msg.to_bytes()
                        print(('SEND UP:<%s>' % txt[:100]))
                        self.UpStr.send(txt)
                        #os.system('netstat | grep 7001')
                        
        def run(self, tmo = -1):
                print ('run(): Sel: %s' % self.Sel.ReadList)
                #os.system('netstat | grep 7001')
                self.Sel.select(tmo)
                #print self.LastPing, time.time()
                if self.LastPing < time.time() - 30:   # ping every 5 minutes
                        if self.UpSock != None:
                                print ('Zinging up...')
                                self.UpStr.zing(1000)                   # disconnect after 15 minutes
                        if self.DnSock != None:
                                print ('Zinging down...')
                                self.DnStr.zing(1000)
                        self.LastPing = time.time()
                        

#
# Callbacks and interface
#

        def haveToken(self):
                #print 'haveToken: token = ', self.Token
                return self.Token != None

        def gotTokenCbk(self):          # virtual
            #print 'Empty gotTokenCbk'
            pass                            
                             
        def messageConfirmedCbk(self, msg):
            pass
            
        def messageReceivedCbk(self, msg):
            pass

        def createMessage(self, src, dst, txt):
            return CMessage(src, dst, txt)
            
        def sendMessage(self, msg):
                forward = True
                if not msg.isBroadcast() and not msg.isPoll():
                        forward = dst == self.Inx or not \
                                self.isCloserUp(dst, self.UpInx)
                if forward:
                        self.sendUp(msg)
                else:
                        raise ChainException("Destination link is not connected")
                return msg

        def waitForToken(self, timeout=None):
            t0 = time.time()
            while not self.haveToken() \
                        and (timeout is None or (time.time() < t0 + timeout)):
                self.needToken()
                dt = 10.0 if timeout is None else min(10.0, t0 + timeout - time.time())
                if dt > 0.0:
                    self.run(dt)
                        
        def run(self, tmo = -1):
                self.Sel.select(tmo)
                if self.LastPing < time.time() - 30:   # ping every 5 minutes
                        if self.UpSock != None:
                                print ('Zinging up...')
                                self.UpStr.zing(1000)                   # disconnect after 15 minutes
                                #print 'UpStr: EOF = %s, Buf = <%s>, LastTxn = %s' % (
                                #       self.UpStr.EOF, self.UpStr.Buf, self.UpStr.LastTxn)
                        if self.DnSock != None:
                                print ('Zinging down...')
                                self.DnStr.zing(1000)
                        self.LastPing = time.time()
                        
        
class ChainLink(ChainSegment):

        def __init__(self, inx, map, callback_delegate, sel):
                ChainSegment.__init__(self, inx, map, sel)
                self.OutMsgList = []
                self.Unconfirmed = {}
                self.CallbackDelegate = callback_delegate
                
        def send(self, dst, text, src = None, send_now = False, need_confirmation = False, insert=False):
                if src == None:
                        src = self.Inx
                msg = self.createMessage(src, dst, text)
                if send_now or self.haveToken():
                        self.sendMessage(msg)
                        if need_confirmation:
                            self.Unconfirmed[msg.MID] = msg
                else:
                        # buffer it
                        if insert:
                            self.OutMsgList.insert(0, (msg, need_confirmation))
                        else:
                            self.OutMsgList.append((msg, need_confirmation))
                        print("message buffered")
                        self.needToken()
                return msg

        def broadcast(self, text, send_now = False, need_confirmation = False, insert=False):
            return self.send(CMessage.Broadcast, text, send_now = send_now, 
                    need_confirmation=need_confirmation, insert=insert)

        def gotTokenCbk(self):
            while self.OutMsgList:
                msg, need_confirmation = self.OutMsgList[0]
                self.OutMsgList = self.OutMsgList[1:]
                self.sendMessage(msg)
                if need_confirmation:
                    self.Unconfirmed[msg.MID] = msg

        def messageConfirmedCbk(self, msg):
            mid = msg.MID
            if mid in self.Unconfirmed:
                del self.Unconfirmed[mid]
                self.CallbackDelegate.messageConfirmed(msg)

        def messageReceivedCbk(self, msg):
            self.CallbackDelegate.messageReceived(msg)
