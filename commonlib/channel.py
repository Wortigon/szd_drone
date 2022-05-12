import threading
import logging
import queue
import time
import commonlib.mavlink as mavlink


class MavlinkMsg:
    lastObj = 0

    def __init__(self, msg):
        self.mav = mavlink.MAVLink(None)
        self.msg = msg
        self.pkt = None
        self.notParsable = False
        self.objNum = MavlinkMsg.lastObj
        MavlinkMsg.lastObj += 1

    def getMsg(self):
        return self.msg

    def getProcessedPacket(self):

        if self.notParsable:
            return None
        if not self.pkt:
            try:
                parsedPacket = self.mav.parse_char(self.msg)
                return parsedPacket
            except Exception:
                self.notParsable = True
                return None

        return self.pkt

    def getJson(self):
        pkt = self.getProcessedPacket()
        if pkt:
            return pkt.to_json()
        return None

    def getId(self):
        packet = self.getProcessedPacket()
        if packet:
            return packet.get_msgId()
        return None


class MavChannelElement():
    def __init__(self, name):
        self.before = None
        self.after = None
        self.name = name
        self.log = logging.getLogger(self.__class__.__name__)

    def setBefore(self, b):
        self.before = b

    def setAfter(self, a):
        self.after = a

    def connectMavElement(self, right):
        self.after = right
        right.before = self

    def send(self, msg):
        self.after.send(msg)

    def receive(self, msg):
        self.before.receive(msg)


class MavChannel(MavChannelElement, threading.Thread):
    def __init__(self, id, name="MavChannel"):
        threading.Thread.__init__(self)
        MavChannelElement.__init__(self, name)
        self.distributor = None
        self.mavChanelElements = list()
        self.endPoint = None
        self.closing = False

    def addDistrib(self, d):
        self.distributor = d
        self.mavChanelElements.append(d)

    def addEndpoint(self, endpoint):
        self.endPoint = endpoint
        self.mavChanelElements[-1].connectMavElement(endpoint)

    def addMavChElement(self, mavElement):
        self.mavChanelElements[-1].connectMavElement(mavElement)
        self.mavChanelElements.append(mavElement)
        if self.endPoint:
            mavElement.connectMavElement(self.endPoint)

    def close(self):
        self.closing = True;

    def run(self):
        while True:
            try:
                msg = self.endPoint.sendingQueue.get(False)
                self.endPoint.sendOut(msg)
            except:
                time.sleep(0.1)
            if self.closing:
                break

    def send(self, msg):
        self.distributor.send(msg)


class MavChannelEndpoint(MavChannelElement):
    def __init__(self, name):
        MavChannelElement.__init__(self, name)
        self.sendingQueue = queue.Queue(maxsize=100)

    def send(self, msg):
        self.sendingQueue.put(msg)

    def sendOut(self, msg):
        pass
