import logging
import threading
import socket
import commonlib.mavlink as mavlink
from datetime import datetime
from commonlib.channel import MavChannelElement, MavChannelEndpoint, MavlinkMsg
import time

# import prctl


class TCPSocketCP(MavChannelEndpoint, threading.Thread):  # used for connecting external application
    def __init__(self, ip="localhost", port=14555, cut=False, name='TCPSocketCP'):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.daemon = True
        self.port = port
        self.ip = ip
        self.conn = None
        self.s = None
        self.cut = cut
        self.log.setLevel(logging.DEBUG)

    def openPort(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.ip, self.port))
        logging.info("Bind to port %d on %s ip" % (self.port, self.ip))
        self.s.listen(1)

    def waitingConnection(self):
        conn, addr = self.s.accept()
        logging.info('Connected on port %d to %s from address %s' % (self.port, self.name, str(addr)))
        self.conn = conn

    def sendOut(self, msg):
        # try:
        if self.conn and not self.cut:
            logging.debug("Sended message on port %d , message: %s  " % (self.port, msg.getJson()))
            self.conn.send(msg.msg)

    def receiveMessages(self):
        try:
            while True:
                pkt = self.conn.recv(1024)
                if not pkt:  # connection closed
                    break

                msg = MavlinkMsg(pkt)
                self.log.debug("Received message on port %d msg: %s" % (self.port, msg.getJson()))
                if not self.cut:
                    self.before.receive(msg)
        finally:
            self.conn.close()
            self.conn = None
            logging.warning("Connection closed on port %d" % (self.port))

    def run(self):
        self.openPort()
        while True:
            self.waitingConnection()
            self.receiveMessages()


class MavProxyConnector(MavChannelEndpoint, threading.Thread):
    def __init__(self, ip='127.0.0.1', port=14551, name='MavProxyConnector'):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.daemon = True
        self.port = port
        self.ip = ip
        self.s = self.connectToMavProxy(port)
        self.addr = (ip, port)
        self.closing = False

    def connectToMavProxy(self, PORT):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', PORT))
        self.log.info('Binded to MavProxy')
        return sock

    def sendOut(self, msg):
        self.s.sendto(msg.msg, self.addr)

    def close(self):
        self.closing = True
        if self.s is not None:
            try:
                self.s.shutdown(socket.SHUT_RDWR)
            except:
                self.log.warning('Trying to shut down disconnected socket')
            self.s.close()
            self.s = None

    def run(self):
        while True:
            if self.closing:
                break
            if self.s is not None:
                data, self.addr = self.s.recvfrom(1024)
                msg = MavlinkMsg(data)
                self.before.receive(msg)




class UDPSocketCP(MavChannelEndpoint):
    def __init__(self, port=14552, name="UDPSocketCP"):
        self.s = self.connect(port)
        MavChannelEndpoint.__init__(self, name)

    def connect(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("127.0.0.1", port))
        return sock


class MissionPlannerUDPCLConnection(MavChannelEndpoint, threading.Thread):
    def __init__(self, port, ip='0.0.0.0', name='MissionPlannerCP'):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.s = self.connect(ip, port)
        self.addr = None

    def connect(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        return sock

    def sendOut(self, msg):
        if self.addr:
            self.log.debug('Sending package to missionplanner')
            self.log.debug("Queue len: " + str(self.sendingQueue.qsize()))
            self.s.sendto(msg.msg, self.addr)
        else:
            self.log.warning("No connection yet!")
            time.sleep(1)

    def run(self):
        self.receiveMsg()

    def receiveMsg(self):
        while True:
            data, self.addr = self.s.recvfrom(1024)
            self.log.debug(data)
            msg = MavlinkMsg(data)
            #json = msg.getJson()
            self.before.receive(msg)


class FilterMavId(MavChannelElement):
    def __init__(self, allowedIdsFromDist=None, allowedIdsFromEndPoint=None, name="FilterMavId"):
        MavChannelElement.__init__(self, name)
        self.allowedIdsFromEndPoint = allowedIdsFromEndPoint
        self.allowedIdsFromDist = allowedIdsFromDist

    def send(self, msg):
        if not self.allowedIdsFromDist:
            self.after.send(msg)
            return
        if msg.getId() in self.allowedIdsFromDist:
            self.after.send(msg)

    def receive(self, msg):
        if not self.allowedIdsFromEndPoint:
            self.before.receive(msg)
            return
        if msg.getId() in self.allowedIdsFromEndPoint:
            self.before.receive(msg)


class PacketPrinter(MavChannelElement):
    nameFromEP = "MAVPacketsFromCopter"
    nameFromDist = "MAVPacketsToCopter"

    def __init__(self, name=''):
        MavChannelElement.__init__(self, name)
        self.name = name
        nameSend = name + self.nameFromDist
        nameReceive = name + self.nameFromEP
        self.fileSend = self.createFile(nameSend)
        self.fileReceive = self.createFile(nameReceive)
        self.mav = mavlink.MAVLink(None)
        self.unknownMessagesReceive = list()
        self.unknownMessagesSend = list()

    def createFile(self, n):
        i = 0
        while True:
            try:
                name = n + '.log'
                if i > 0:
                    name = n + str(i) + '.log'
                open(name, 'r')
                self.log.debug('File name %s already used' % name)
                i += 1
            except IOError:
                self.log.info("Log file %s created" % name)
                return open(name, 'w')

    def send(self, msg):
        toFile = "Id: %s json: %s" % (str(msg.getJson()), str(msg.getId()))
        self.fileSend.write(toFile)
        self.fileSend.write('\n')

        self.after.send(msg)

    def receive(self, msg):
        # try:
        #     pkt = self.mav.parse_char(msg.msg)
        #     if not pkt:
        #         self.log.warning("Cant parse message in PacketPrinter(%s)" % msg.msg)
        #     else:

        # except mavlink.MAVError as e:
        #     if e not in self.unknownMessagesReceive:
        #         self.unknownMessagesReceive.append(e)
        toFile = "Id: %s json: %s" % (str(msg.getJson()), str(msg.getId()))
        self.fileReceive.write(toFile)
        self.fileReceive.write('\n')

        self.before.receive(msg)

    def writeUnknownMsg(self, unknownMessages, file):
        file.write('\n\n')
        for m in unknownMessages:
            file.write(m + "\n")

    def close(self):

        self.writeUnknownMsg(self.unknownMessagesReceive, self.fileReceive)
        self.writeUnknownMsg(self.unknownMessagesSend, self.fileSend)
