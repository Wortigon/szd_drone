import logging
import threading
import socket
import json
import time


from commonlib import mavlink
from datetime import datetime
from commonlib.channelComponents import PacketPrinter

from commonlib.channel import MavChannelEndpoint, MavChannelElement, MavlinkMsg
from commonlib.mysql.mysqlBase import MySQLBase

import copterproxylib.lte.secure as secure
add_data = "INSERT INTO CopterData ({0}) VALUES({1})"


class MySqlCopterDataEP(MavChannelEndpoint):
    neededMavIds = [0, 33, 24, 74]  # HEARTBEAT(mode), GLOBAL_POSITION_INT(relative_alt, lon, lat), GPS_RAW_INT(satelites, h_acc(position uncert))
    modeDict = {0: 'STABILIZE', 1: 'ACRO', 2: 'ALT_HOLD', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 7: 'CIRCLE', 9: 'LAND', 11: 'DRIFT', 13: 'SPORT', 14: 'FLIP', 15: 'AUTOTUNE', 16: 'POSHOLD', 17: 'BRAKE', 18: 'THROW', 19: 'AVOID_ADSB', 20: 'GUIDED_NOGPS', 21: 'SMART_RTL'}

    def __init__(self, sendingInterval=5, name='MySqlCopterDataEP'):
        MavChannelEndpoint.__init__(self, name)
        # self.log.setLevel(logging.DEBUG)
        self.db = MySQLBase()
        self.db.connect(user=secure.mysqlUsr, password=secure.mysqlPass, host=secure.host, database=secure.database)
        self.lastSendingTime = time.time()
        self.sendingInterval = sendingInterval
        self.messageDict = dict()
        # self.lastIdQuery = "select LAST_INSERT_ID() from CopterData;"

        self.attrList = [('time', self.getTime, ()),
                         ('altitude', self.getParamFromMavlink, (33, 'relative_alt', 1000)),
                         ('speed', self.getParamFromMavlink, (74, 'groundspeed', 100)),
                         ('longitude', self.getParamFromMavlink, (33, 'lon')),
                         ('latitude', self.getParamFromMavlink, (33, 'lat')),
                         ('satelites_visible', self.getParamFromMavlink, (24, 'satellites_visible')),
                         ('pos_uncertanity', self.getParamFromMavlink, (24, 'h_acc')),
                         ('mode', self.getMode, ())]

    def sendOut(self, msg):
        if None == msg.getId():
            return
        self.log.debug(str(msg.getId()))
        self.messageDict[msg.getId()] = msg.getJson()
        if msg.getId() is 0:
            self.log.info("Mode: " + self.getMode())
        if (self.lastSendingTime + self.sendingInterval) < time.time():
            self.log.debug("Sending time")
            self.uploadToDB()

    def uploadToDB(self):
        self.lastSendingTime = time.time()
        self.log.debug("getTime: " + str(self.attrList[0][1]))
        self.log.debug(tuple(i[1] for i in self.attrList))
        self.db.insert(add_data.format(','.join([i[0] for i in self.attrList]), ','.join(['%s' for i in xrange(len(self.attrList))])), tuple(i[1](*i[2]) for i in self.attrList))

    def getTime(self):
        return MySQLBase.getTime()

    def getMode(self):
        modeID = self.getParamFromMavlink(0, 'custom_mode')
        mode = self.modeDict.get(modeID)
        if not mode:
            return "UNKID: " + str(modeID)
        return mode

    def getParamFromMavlink(self, mavId, jsonId, div=1):
        js = self.messageDict.get(mavId)
        if not js:
            return None

        return json.loads(js)[jsonId] / float(div)


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
        # self.log.setLevel(logging.DEBUG)

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info('Trying to connect to server!')
        self.s.connect((self.ip, self.port))
        self.connected = True
        self.log.info('Connected to server')

        while True:
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

