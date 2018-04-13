#!/usr/bin/env python
import requests
from time import time, sleep
from json import dumps
from ConfigParser import RawConfigParser
from RouterEndpointMap import RouterEndpointMap

from zenApiLib import ZenAPIConnector

class ZenAPIConfig():
    '''
    This class reads a file called 'creds.cfg' and generates a config that
    is then used to connect to the Zenoss API. See the sample creds.cfg
    file in the repo @ https://github.com/amccurdy/zenoss_api for more
    information.
    '''
    def __init__(self):
        self.config = RawConfigParser()
        self.config.read('/root/zenoss_api/creds.cfg')
        self.url = self.config.get('zenoss_api', 'url')
        self.username = self.config.get('zenoss_api', 'username')
        self.password = self.config.get('zenoss_api', 'password')
        self.ssl_verify = self.config.get('zenoss_api', 'ssl_verify')
        self.router_endpoints = RouterEndpointMap()

    def getUrl(self):
        return self.url

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getSSLVerify(self):
        if self.ssl_verify == None:
            return False
        try: 
            if self.ssl_verify.lower() == 'true':
                return True
            elif self.ssl_verify.lower() == 'false':
                return False
            else:
                # default to True if they set anything other than "true" or "false"
                return True
        except AttributeError:
            # TODO: add exception handling if something other than a string exists here
            raise

    def getRouterEndpoint(self, router_name):
        return self.router_endpoints.getEndpoint(router_name)


class ZenAPIConnector_v1():
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


class ZenDeviceUuidFinder():
    '''
    This class returns the name and UUID of a device when
    provided a query
    '''
    def __init__(self, query):
        self.router = 'DeviceRouter'
        self.method = 'getDeviceUuidsByName'
        self.query = query
        self.uuid = None
        self.data = {'query': self.query}
        self.api_call = ZenAPIConnector(self.router,
                                        self.method,
                                        self.data)
        self.response = self.api_call.send()
        self.response_json = self.response.json()
        self.count = len(self.response_json['result']['data'])

    def getFirstUuid(self):
        try:
            return self.response_json['result']['data'][0]['uuid']
        except (KeyError, TypeError):
            return None

    def getAllUuids(self):
        try:
            return [x['uuid'] for x in self.response_json['result']['data']]
        except (KeyError, TypeError):
            return None

    def getCount(self):
        return self.count

    def first(self):
        return self.getFirstUuid()


class ZenDeviceUidFinder():
    '''
    This class returns the name and UID (path) of a device when
    provided a query
    '''
    def __init__(self, name=None, ip=None):
        self.router = 'DeviceRouter'
        self.method = 'getDevices'
        self.params = {}
        if name is not None:
            self.params['name'] = name
        if ip is not None:
            self.params['ipAddress'] = ip
        self.data = {'params': self.params}
        self.api_call = ZenAPIConnector(self.router,
                                        self.method,
                                        self.data)
        self.response = self.api_call.send()
        self.response_json = self.response.json()
        self.count = len(self.response_json['result']['devices'])

    def getFirstUid(self):
        try:
            return self.response_json['result']['devices'][0]['uid']
        except (KeyError, TypeError):
            return None

    def getAllUids(self):
        try:
            return [x['uid'] for x in self.response_json['result']['devices']]
        except (KeyError, TypeError):
            return None

    def getCount(self):
        return self.count

    def first(self):
        return self.getFirstUid()


class ZenJobsWatcher():
    '''
    This class is instantiated with a job id. Its primary purpose
    is to allow a user to perform a set of tasks that may require
    a job to complete before moving on to another task.
    '''
    def __init__(self):
        self.router = 'JobsRouter'

    def checkJobStatus(self, jobid):
        self.method = 'getInfo'
        self.data = {'jobid': jobid}
        api = ZenAPIConnector(self.router, self.method, self.data)
        result = api.send()
        try:
            status = result.json()['result']['data']['status']
        except (KeyError, ValueError):
            status = 'UNKNOWN! Invalid Job ID or other failure'
        return status

    def watchStatus(self, jobid, timeout):
        '''
        This is a blocking method that will check on the status of
        a job every n seconds until it's either completed, aborted,
        failed, or a timeout is reached. It returns a tuple with the
        success status of the job, and a bool for Success or Failure
        '''
        self.success = 'Unknown'
        starttime = time()
        while self.success != 'SUCCESS':
            currtime = time()
            self.success = self.checkJobStatus(jobid)
            if starttime + timeout <= currtime:
                self.success = 'TIMEOUT'
                break
            elif self.success == 'ABORTED':
                break
            sleep(3)
        if self.success == 'FAILURE':
            return self.success, False
        elif self.success == 'ABORTED':
            return self.success, False
        elif self.success == 'TIMEOUT':
            return self.success, False
        elif self.success == 'SUCCESS':
            return self.success, True


if __name__ == '__main__':
    pass
