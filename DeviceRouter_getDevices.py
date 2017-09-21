#!/usr/bin/env python
import sys
from ZenAPIConnector import ZenAPIConnector

router = 'DeviceRouter'


def getDevices():
    method = 'getDevices'
    data = {'limit': 200}
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    data = response.json()['result']
    return data


def deviceReport():
    device_resp = getDevices()
    devices = device_resp['devices']
    print 'Name, IP Address, UID, ProdState, Collector, Location'
    for dev in devices:
        try: 
            location = dev['location']['uid']
        except (KeyError, TypeError): 
            location = ''
        print '%s, %s, %s, %s, %s, %s' % (dev['name'], 
                                          dev['ipAddressString'],
                                          dev['uid'],
                                          dev['productionState'],
                                          dev['collector'],
                                          location)


if __name__ == '__main__':
    deviceReport()
