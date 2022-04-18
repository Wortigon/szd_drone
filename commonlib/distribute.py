import socket
import threading
import logging
from commonlib.channel import *


class Distributor():
    def __init__(self, name="Distributor"):
        self.registeredChannelsEast = list()
        self.registeredChannelsWest = list()
        self.log = logging.getLogger(self.__class__.__name__)

    def createNewChannelWest(self, id=''):
        ch = MavChannel(id)
        self.addChannelWest(ch)
        return ch

    def createNewChannelEast(self, id=''):
        ch = MavChannel(id)
        self.addChannelEast(ch)
        return ch

    def addChannelWest(self, ch):
        ch.addDistrib(DistributeWest(self))
        self.registeredChannelsWest.append(ch)
        self.log.info("Adding channel to west")

    def addChannelEast(self, ch):
        ch.addDistrib(DistributeEast(self))
        self.registeredChannelsEast.append(ch)
        self.log.info("Adding channel to east")

    def startThreads(self):
        for ch in self.registeredChannelsEast:
            self.startAllinCh(ch)
        for ch in self.registeredChannelsWest:
            self.startAllinCh(ch)

    def startAllinCh(self, ch):
        ch.daemon = True
        ch.start()
        if isinstance(ch.endPoint, threading.Thread):
            ch.endPoint.daemon = True
            ch.endPoint.start()
            self.log.info("Starting thread " + str(type(ch.endPoint)))

    def sendToEast(self, msg):
        for regCh in self.registeredChannelsEast:
            regCh.send(msg)

    def sendToWest(self, msg):
        for regCh in self.registeredChannelsWest:
            regCh.send(msg)


class DistributeWest(MavChannelElement):
    def __init__(self, dist, name="DistributeWest"):
        MavChannelElement.__init__(self, name)
        self.distributor = dist

    def receive(self, msg):
        self.distributor.sendToEast(msg)


class DistributeEast(MavChannelElement):
    def __init__(self, dist, name="DistributeEast"):
        MavChannelElement.__init__(self, name)
        self.distributor = dist

    def receive(self, msg):
        self.distributor.sendToWest(msg)
