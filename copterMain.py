#!/usr/bin/python
import time
import subprocess32
import sys
import os
from commonlib.distribute import Distributor
from commonlib.channelComponents import *

from copterproxylib.copterChannelComponents import TCPClientEP

import commonlib.secure as secure

mavproxy = None
distributor = None
serverEP = None

def checkMAVProxyConnection():
    global mavproxy
    isMavProxyAlive = mavproxy is not None and mavproxy.poll() is None        
    if isMavProxyAlive:
        logging.info("Mavproxy is alive poll result is: %s" % mavproxy.poll())
    else:
        reason = None
        if mavproxy is None:
            reason = 'mavproxy is "none"'
        else:
            if mavproxy.poll() is 1:
                reason = "Mavproxy exited with error code: 1"
            else:
                reason = 'mavproxy has no response or is disconnected'
        logging.info("Mavproxy is dead. Reason: %s" % reason)
    return isMavProxyAlive

def checkServerConnection():
    global serverEP
    isServerConnectionAlive = serverEP is not None and (serverEP.connected == True) and (serverEP.delta < 5000)
    if isServerConnectionAlive:
        logging.info("Server Connection is alive")
    else:
        logging.info("Server Connection is dead")
    return isServerConnectionAlive

def checkConnectionState():
    logging.info("checking connections")
    return checkMAVProxyConnection() and checkServerConnection()

def closeMAVProxyConnection():
    global mavproxy
    if mavproxy is not None:
        mavproxy.terminate()
        mavproxy = None

def closeDistributor():
    global distributor
    if distributor is not None:
        distributor.close()
        distributor = None

def closeConnection():
    closeMAVProxyConnection()
    closeDistributor()

def initializeMAVProxyConnection():
    global mavproxy
    logging.info("initializing MAVProxy")
    os.setgid(0)
    os.setuid(0)
    #removed params
    #"--logfile", "/home/rtd/mavpro.log",
    mavproxy = subprocess32.Popen(["/usr/bin/python3", "/usr/local/bin/mavproxy.py", "--master=" + secure.master, "--baudrate", "57600", "--out", "127.0.0.1:14551", "--aircraft", "/home/rtd/MyCopter/", "--daemon"], start_new_session=True, stdout=subprocess32.PIPE, stdin=None, shell=False)
    try:
        #"""
        result = mavproxy.communicate(timeout=5)[0]
        resultstr = result.decode('ascii')
        logging.info("communicate call result: {%s}" % resultstr)
        if "Failed" in resultstr:
            logging.error("Failed to connect mavproxy: {%s}" % result)
            raise RuntimeError("Failed to connect mavproxy: {%s}" % result)
        #"""
        if checkMAVProxyConnection():
            logging.info("MAVProxy initialised")
        else:
            logging.info("Failed to initialise MAVProxy")
    except subprocess32.TimeoutExpired:
        logging.error("MAVProxy runs as expected")

def initializeDistributor():
    global distributor, serverEP
    distributor = Distributor()

    chMavProxy = distributor.createNewChannelWest()
    chMavProxy.addEndpoint(MavProxyConnector())

    chServer = distributor.createNewChannelEast()
    serverEP = TCPClientEP(ip=secure.serverIP, port=5005)
    chServer.addEndpoint(serverEP)

    distributor.startThreads()

def waitForServer():
    temp = 0
    while serverEP.connected is False:
        logging.info("waiting for TCP connection")
        time.sleep(1)
        temp+=1
        if temp > 5:
            break

def resetMAVProxyConnection():
    if not checkMAVProxyConnection():
        logging.warning("reseting MAVProxy connection")
        closeMAVProxyConnection()
        initializeMAVProxyConnection()

def resetDistributor():
    if not checkServerConnection():
        logging.warning("reseting distributor connection")
        closeDistributor()
        initializeDistributor()

def resetConnection():
    resetMAVProxyConnection()
    resetDistributor()


def main():
    logging.basicConfig(format='%(asctime)s - [%(module)s.%(name)s.%(funcName)s():%(lineno)i] - %(levelname)s: %(message)s', level=logging.INFO)
    # with open('./mavproxy.log', 'w') as outfile:

    try:
        while True:
            try:
                logging.info("\r\n\r\n\r\n*********************************************************************\r\n")
                if not checkConnectionState():
                    resetConnection()
                    waitForServer()
                time.sleep(1)
            except KeyboadrInterrupt:
                raise
            except Exception as e:
                self.log.debug("caught an exception: %s" % str(e))
    except KeyboardInterrupt:
        closeConnection()
        sys.exit(0)



if __name__ == "__main__":
    main()

