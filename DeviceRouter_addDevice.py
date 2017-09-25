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
method = 'addDevice'

usage = '%s <device_id> <device_class_name> <productionState>' % (sys.argv[0])

def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)

def buildArgs():
    if len(sys.argv) != 4:
        fail()
    else:
        try:
            device = sys.argv[1]
            deviceClass = sys.argv[2]
            productionState = sys.argv[3]
        except:
            fail()
    data = {'deviceName': device, 'deviceClass': deviceClass, 'productionState': productionState}
    return data

def addDevice(data):
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data

if __name__ == '__main__':
    data = buildArgs()
    api_response = addDevice(data)
    print api_response
