import sys
import pprint
import requests
import xmltodict


class HuaweiE3372(object):
  BASE_URL = 'http://{host}'
  COOKIE_URL = '/html/index.html'
  XML_APIS = [
      '/api/device/information',
      '/api/device/signal',
      '/api/monitoring/status',
      '/api/monitoring/traffic-statistics',
      '/api/dialup/connection',
      '/api/global/module-switch',
      '/api/net/current-plmn',
      '/api/net/net-mode',
  ]
  session = None

  def __init__(self, host='192.168.8.1'):
    self.host = host
    self.base_url = self.BASE_URL.format(host=host)
    self.session = requests.Session()
    # get a session cookie by requesting the COOKIE_URL
    r = self.session.get(self.base_url + self.COOKIE_URL)

  def get(self, path):
    return xmltodict.parse(self.session.get(self.base_url + path).text).get('response', None)
