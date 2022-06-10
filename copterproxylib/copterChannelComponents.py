import logging
import threading
import socket
import json
import time


from commonlib import mavlink
from datetime import datetime
from commonlib.channelComponents import PacketPrinter

from commonlib.channel import MavChannelEndpoint, MavChannelElement, MavlinkMsg

import copterproxylib.lte.secure as secure

class MavProxyConnector(MavChannelEndpoint, threading.Thread):
    def __init__(self, ip='127.0.0.1', port=14551, name='MavProxyConnector'):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.daemon = True
        self.port = port
        self.ip = ip
        self.s = self.connectToMavProxy(port)
        self.addr = (ip, port)
        # self.dist = dist

        # dist.setBefore(self)

    def connectToMavProxy(self, PORT):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', PORT))
        self.log.info('Binded to MavProxy')
        return sock

    def sendOut(self, msg):
        self.s.sendto(msg.msg, self.addr)

    def run(self):
        self.receiveMessages()

    def receiveMessages(self):
        while True:
            data, self.addr = self.s.recvfrom(1024)
            msg = MavlinkMsg(data)
            self.dist.send(msg)
            # self.log.debug("Received message from mav proxy")


class TCPClientEP(MavChannelEndpoint, threading.Thread):
    def __init__(self, ip, port, name="TCPSocketClient"):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.daemon = True
        self.port = port
        self.ip = ip
        self.s = None
        self.connected = False
        self.delta = None
        # self.log.setLevel(logging.DEBUG)

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info('Trying to connect to server!')
        self.s.connect((self.ip, self.port))
        self.connected = True
        self.log.info('Connected to server')
        
        lastTimestamp = datetime.now()
        while True:
            new = datetime.now()
            self.delta = (new - lastTimestamp).total_seconds() * 1000
            lastTimestamp = new
            pkt = self.s.recv(1024)
            msg = MavlinkMsg(pkt)
            self.log.debug('Received message on port %d' % self.port)
            self.before.receive(msg)

    def sendOut(self, msg):
        if self.connected:
            self.s.send(msg.msg)
            self.log.debug("Sended message on port %d" % self.port)


# class UDPSocketCP(MavChannelEndpoint):
#     def __init__(self, port=14552, name="UDPSocketCP"):
#         self.s = self.connect(port)
#         MavChannel.__init__(self, name)

#     def connect(self, port):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.connect(("127.0.0.1", port))
#         return sock

