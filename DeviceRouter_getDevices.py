#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of devices and display device-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'DeviceRouter'
method = 'getDevices'
data = {'limit': 200}

def getDevices():
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


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
