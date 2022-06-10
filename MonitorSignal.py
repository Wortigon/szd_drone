import subprocess
import datetime
import time
import sys

def getFlightNumber():
    f = open("/home/rtd/szd_drone/flightNumber", "r")
    flightNumber = f.readline()
    f.close()
    f = open("/home/rtd/szd_drone/flightNumber", "w")
    tmp = int(flightNumber) + 1
    f.write(str(tmp))
    f.close()
    return flightNumber

def runShellScript(shellScript):
    return subprocess.run([shellScript], stdout=subprocess.PIPE).stdout.decode('utf-8')

def checkValidity(fn):
    if ' 0 seconds' in open("/home/rtd/szd_drone/signalLogs/flight" + fn + ".txt").read():
        return False
    return True
    

def main():
    global timestamp, result, flightNumber
    try:
        flightNumber = getFlightNumber()
        runShellScript("/home/rtd/szd_drone/testConnection.sh")
        setupmsg = runShellScript("/home/rtd/szd_drone/setupConnectionMonitor.sh")
        print(setupmsg + "\r\nStarting to log data:\r\n")
        while(True):
            result = runShellScript("/home/rtd/szd_drone/testConnection.sh")
            timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            f = open("/home/rtd/szd_drone/signalLogs/flight" + flightNumber + ".txt", 'a')
            f.write(timestamp + '\r\n' + result) 
            f.close()
            print(timestamp + '\r\n' + result)
            if not checkValidity(flightNumber):
                runShellScript("/home/rtd/szd_drone/connectionLoggingRestart.sh")
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
        
if __name__ == "__main__":
    main()
