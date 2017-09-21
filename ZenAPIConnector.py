#!/usr/bin/env python
import requests
from json import dumps
from ConfigParser import RawConfigParser


class ZenAPIConfig():
    def __init__(self):
        self.config = RawConfigParser()
        self.config.read('creds.cfg')
        self.url = self.config.get('zenoss_api', 'url')
        self.username = self.config.get('zenoss_api', 'username')
        self.password = self.config.get('zenoss_api', 'password')
        self.ssl_verify = bool(self.config.get('zenoss_api', 'ssl_verify'))

    def getUrl(self):
        return self.url

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getSSLVerify(self):
        return self.ssl_verify


class ZenAPIConnector():
    def __init__(self, router, router_endpoint, method, data):
        self.config = ZenAPIConfig()
        self.url = self.config.getUrl()
        self.router = router
        self.router_endpoint = router_endpoint
        self.api_endpoint = self.url + self.router_endpoint
        self.method = method
        self.username = self.config.getUsername()
        self.password = self.config.getPassword()
        self.headers = {'Content-Type': 'application/json'}
        self.ssl_verify = self.config.getSSLVerify()
        self.data = data
        self.payload = dumps({'action': self.router,
                              'method': self.method,
                              'data': [data],
                              'tid': 1})

    def send(self):
        response = requests.post(self.api_endpoint,
                                 self.payload,
                                 headers=self.headers,
                                 auth=(self.username, self.password),
                                 verify=self.ssl_verify)
        if response.status_code == 200:
            return response
        else:
            print 'HTTP Status: %s' % (response.status_code)

if __name__ == '__main__':
    pass
