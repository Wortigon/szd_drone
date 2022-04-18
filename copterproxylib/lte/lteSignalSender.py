import threading
import time
import copterproxylib.lte.e3372
from commonlib.mysql.mysqlBase import MySQLBase
import commonlib.secure
import logging


add_data = "INSERT INTO LTESignal ({0}) VALUES({1})"
add_starting_time = "INSERT INTO StartTime (start_time) VALUES(%s)"


class LTESignalSender(threading.Thread):
  def __init__(self, sendingInterval=5):
    threading.Thread.__init__(self)
    self.daemon = True
    self.sendingInterval = sendingInterval
    self.db = MySQLBase()
    self.db.connect(secure.mysqlUsr, secure.mysqlPass, secure.host, secure.database)
    self.attrList = ['time', 'copter_data_id', 'cell_id', 'pci', 'rsrq', 'rsrp', 'rssi', 'sinr']
    self.lteModem = HuaweiE3372()
    logging.basicConfig(level=logging.WARNING)

  def run(self):
    self.sendStartingTime()
    while True:
      try:
        self.send()
      except Exception as e:
        print(e)

      time.sleep(self.sendingInterval)

  def send(self):
    d = self.getSignalDict()
    params = list()
    params.append(MySQLBase.getTime())
    params.append(self.db.getLastIdCopterData())
    for attr in self.attrList[2:]:
      n = d[attr].find('d')
      if n > 0:
        value = d[attr][:n]
      else:
        value = d[attr]

      if not representsInt(value):
        logging.warning('Not an integer from LTE modem: ' + value)
        value = None
      params.append(value)

    self.db.insert(add_data.format(','.join(self.attrList), '%s,%s,%s,%s,%s,%s,%s,%s'), tuple(params))

  def sendStartingTime(self):
    self.db.insert(add_starting_time, (MySQLBase.getTime(),))

  def getSignalDict(self):
    return self.lteModem.get('/api/device/signal')


def representsInt(s):
  try:
    int(s)
    return True
  except ValueError:
    return False
