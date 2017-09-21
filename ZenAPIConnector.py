#!/usr/bin/env python
import requests
from json import loads, dumps
from pprint import pprint

class ZenAPIConnector():
    def __init__(self, url, router, router_endpoint, method, username, password, ssl_verify, data):
        self.url = url
        self.router = router
        self.router_endpoint = router_endpoint
        self.api_endpoint = url + router_endpoint
        self.method = method
        self.username = username
        self.password = password
        self.headers = {'Content-Type': 'application/json'}
        self.ssl_verify = ssl_verify
        self.data = data
        self.payload = dumps({'action': self.router, 'method': self.method, 'data': [data], 'tid': 1})

    def send(self):
        response = requests.post(self.api_endpoint, self.payload, headers=self.headers,
                                 auth=(self.username, self.password), verify=self.ssl_verify)
        if response.status_code == 200:
            return response
        else:
            print 'HTTP Status: %s' % (response.status_code)

if __name__ == '__main__':
#    api = ZenAPIConnector(url, router, router_endpoint, method, username, password, ssl_verify, data)
#    resp = api.send()
#    print resp.json()
#    pprint(api.getAllRouters())
    pass
