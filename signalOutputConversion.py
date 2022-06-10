import datetime
import time
import sys

myfile = "flight4"
myformat = ".txt"

def getValueFromRow(row, start):
    temp = ""
    for x in range(start, len(row)-1):
        temp += row[x]
    return getIntValueOfVariable(replaceDotWithComa(temp))

def getIntValueOfVariable(var):
    temp = var.split()
    return temp[0]

def replaceDotWithComa(var):
    if "." in var:
        temp = var.split('.')
        temp2 = temp[0] + "," + temp[1]
        return temp2
    else:
        return var

def main():
    inFile = open(myfile+myformat, 'r')
    Lines = inFile.readlines()
    inFile.close()
    outfile = open(myfile+"_converted"+myformat, 'w')
    outfile.write("timestamp\trssi(dBm)\trsrq(dB)\trsrp(dBm)\tsnr(dB)\tnoise(dBm)\n")
    outfile.close()

    timestamp = None
    rssi = None
    rsrq = None
    rsrp = None
    snr = None
    noise = None

    lineOfBlock = 0

    for line in Lines:
        if line[0] != ' ':
            timestamp = getValueFromRow(line, 11)
            lineOfBlock = 0
        if line[0] == ' ':
            lineOfBlock += 1
            if lineOfBlock == 4:
                rssi = getValueFromRow(line, 25)
            if lineOfBlock == 5:
                rsrq = getValueFromRow(line, 25)
            if lineOfBlock == 6:
                rsrp = getValueFromRow(line, 25)
            if lineOfBlock == 7:
                snr  = getValueFromRow(line, 25)
                outfile = open(myfile+"_converted"+myformat, 'a')
                outfile.write(timestamp +"\t"+ rssi +"\t"+ rsrq +"\t"+ rsrp +"\t"+ snr + "\n")
                outfile.close()
                lineOfBlock = 0


if __name__ == "__main__":
    main()