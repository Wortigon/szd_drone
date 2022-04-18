#!/usr/bin/python


from baseproxylib.baseChannelComponents import *
import time
import logging
from commonlib.distribute import Distributor

def main():
    logging.basicConfig(format='%(asctime)s - [%(module)s.%(name)s.%(funcName)s():%(lineno)i] - %(levelname)s: %(message)s', level=logging.INFO)

    distributor = Distributor()

    chMP = distributor.createNewChannelEast()
    chMP.addEndpoint(MissionPlannerUDPCLConnection(port=14550))

    chCopterTCP = distributor.createNewChannelWest()
    chCopterTCP.addEndpoint(TCPServerEP(port=5005))

    distributor.startThreads()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
