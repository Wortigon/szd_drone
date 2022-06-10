#!/usr/bin/python


from baseproxylib.baseChannelComponents import *
import time
import logging
import sys
from commonlib.distribute import Distributor

distributor = None

def closeDistributor():
    global distributor
    if distributor is not None:
        distributor.close()
        distributor = None

def initializeDistributor():
    global distributor
    distributor = Distributor()

    chMP = distributor.createNewChannelEast()
    chMP.addEndpoint(MissionPlannerUDPCLConnection(port=14550))

    chCopterTCP = distributor.createNewChannelWest()
    chCopterTCP.addEndpoint(TCPServerEP(port=5005))

    distributor.startThreads()

def main():
    logging.basicConfig(format='%(asctime)s - [%(module)s.%(name)s.%(funcName)s():%(lineno)i] - %(levelname)s: %(message)s', level=logging.INFO)

    initializeDistributor()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        closeDistributor()
        sys.exit(0)


if __name__ == "__main__":
    main()
