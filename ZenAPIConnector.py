#!/usr/bin/env python
import requests
from json import dumps
from ConfigParser import RawConfigParser
from RouterEndpointMap import RouterEndpointMap


class ZenAPIConfig():
    '''
    This class reads a file called 'creds.cfg' and generates a config that
    is then used to connect to the Zenoss API. See the sample creds.cfg
    file in the repo @ https://github.com/amccurdy/zenoss_api for more
    information.
    '''
    def __init__(self):
        self.config = RawConfigParser()
        self.config.read('creds.cfg')
        self.url = self.config.get('zenoss_api', 'url')
        self.username = self.config.get('zenoss_api', 'username')
        self.password = self.config.get('zenoss_api', 'password')
        self.ssl_verify = bool(self.config.get('zenoss_api', 'ssl_verify'))
        self.router_endpoints = RouterEndpointMap()

    def getUrl(self):
        return self.url

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getSSLVerify(self):
        return self.ssl_verify

    def getRouterEndpoint(self, router_name):
        return self.router_endpoints.getEndpoint(router_name)


class ZenAPIConnector():
    '''
    This class is instantiated with a router, method, and a data
    dictionary. The router endpoint URL is pulled from the
    RouterEndpointMap class.
    '''
    def __init__(self, router, method, data):
        self.config = ZenAPIConfig()
        self.url = self.config.getUrl()
        self.router = router
        self.router_endpoint = self.config.getRouterEndpoint(self.router)
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
