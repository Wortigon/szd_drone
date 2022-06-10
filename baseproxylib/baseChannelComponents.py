from commonlib.channelComponents import PacketPrinter, FilterMavId, MissionPlannerUDPCLConnection
from commonlib.channel import MavChannelEndpoint, MavChannelElement, MavlinkMsg

import threading
import websocket
import json
import socket
import logging
import commonlib.secure

class TCPServerEP(MavChannelEndpoint, threading.Thread):
    def __init__(self, ip="0.0.0.0", port=14555, cut=False, name='TCPServerEP'):
        threading.Thread.__init__(self)
        MavChannelEndpoint.__init__(self, name)
        self.daemon = True
        self.port = port
        self.ip = ip
        self.conn = None
        self.s = None
        self.cut = cut
        #self.log.setLevel(logging.DEBUG)

    def openPort(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.ip, self.port))
        logging.info("Bind to port %d on %s ip" % (self.port, self.ip))
        self.s.listen(1)

    def closePort(self):
        if self.s is not None:
            self.s.shutdown()
            self.s.close()
            self.s = None

    def waitingConnection(self):
        conn, addr = self.s.accept()
        logging.info('Connected on port %d to %s from address %s' % (self.port, self.name, str(addr)))
        self.conn = conn

    def send(self, msg):
        # try:
        if self.conn and not self.cut:
            logging.debug("Sent message on port %d " % self.port)
            self.conn.send(msg.msg)

    def sendOut(self, msg):
        self.send(msg)

    def receiveMessages(self):
        try:
            while True:
                pkt = self.conn.recv(1024)
                if not pkt:  # connection closed
                    break

                msg = MavlinkMsg(pkt)
                self.log.debug("Received message on port %d" % self.port)
                if not self.cut:
                    self.before.receive(msg)
        finally:
            self.conn.close()
            self.conn = None
            logging.warning("Connection closed on port %d" % self.port)

    def run(self):
        try:
            self.openPort()
            while True:
                try:
                    self.waitingConnection()
                    self.receiveMessages()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self.log.warning("caught an exception: %s" % str(e))
        except KeyboardInterrupt:
            raise
        finally:
            self.closePort()




class PacketPrinterBase(PacketPrinter):
    nameFromEP = "MAVPacketsToMPlanner"
    nameFromDist = "MAVPacketsFromMPlanner"
