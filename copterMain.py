#!/usr/bin/python
import time
import subprocess32
import sys
from commonlib.distribute import Distributor
from commonlib.channelComponents import *
from copterproxylib.lte.lteSignalSender import LTESignalSender

from copterproxylib.copterChannelComponents import MySqlCopterDataEP, TCPClientEP

import commonlib.secure as secure

mySQLLteLogStart = True
mySQLCopterDataLogStart = True

loraToSendMavID = [0, 33]


def main():
    logging.basicConfig(format='%(asctime)s - [%(module)s.%(name)s.%(funcName)s():%(lineno)i] - %(levelname)s: %(message)s', level=logging.INFO)
    # with open('./mavproxy.log', 'w') as outfile:
    mavproxy = subprocess32.Popen(
        "start cmd /c mavproxy.py --master=COM6 --baudrate 57600 --out 127.0.0.1:14551 --aircraft ./MyCopter",
        stdout=subprocess32.PIPE, stdin=None, shell=True)
    try:
        logging.error('before communicate')
        result = mavproxy.communicate(timeout=5)[0]
        resultstr = result.decode('UTF-8')
        logging.error('itt vagyunk {%s}' % resultstr)

        if "Failed" in resultstr:
            logging.error('Failed to connect mavproxy: {%s}' % result)
            raise RuntimeError("Failed to connect mavproxy: {%s}" % result)
    except subprocess32.TimeoutExpired:

        logging.debug("No problem with mavproxy")

    try:
        distributor = Distributor()

        #if mySQLCopterDataLogStart:
        #    chSql = distributor.createNewChannelEast()
        #    chSql.addMavChElement(FilterMavId(allowedIdsFromDist=MySqlCopterDataEP.neededMavIds))
        #    chSql.addEndpoint(MySqlCopterDataEP())

        #if mySQLLteLogStart:
        #    lte = LTESignalSender()
        #    lte.start()

        chMavProxy = distributor.createNewChannelWest()
        chMavProxy.addEndpoint(MavProxyConnector())

        chServer = distributor.createNewChannelEast()

        serverEP = TCPClientEP(ip=secure.serverIP, port=5005)
        chServer.addEndpoint(serverEP)
        #missionPlannerCP = MissionPlannerUDPCLConnection('0.0.0.0', port=14555)

        # chMP.addMavChElement(PacketPrinter())
        # chMP.addEndpoint(missionPlannerCP)

        # chMP2 = distributor.createNewChannelEast()
        # missionPlannerCP2 = MissionPlannerUDPCLConnection('0.0.0.0')
        # chMP.addMavChElement(FilterMavId([0]))

        # chMP2.addEndpoint(missionPlannerCP2)

        # lora = LoraCP()
        # p1 = PacketPrinter('before')
        # p2 = PacketPrinter('after')

        # f = FilterMavId([33, 0])
        # p1.connectFromRight(f)

        # f.connectFromRight(p2)
        # p2.connectFromRight(lora)

        # distributor.addChannel(p1)
        # #tcpConnPoint = TCPSocketCP()
        # # distributor.addChannel(tcpConnPoint)
        # # TODO: make it work with domain 'norbi-acer'
        # tcpClient = TCPSocketClient(ip='localhost', port=5005)

        # distributor.addChannel(tcpClient)
        distributor.startThreads()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mavproxy.kill()

        sys.exit(0)


if __name__ == "__main__":
    main()
    # trying db
    # db = MySqlCopterDataEP()
    # print db.getLastId()
