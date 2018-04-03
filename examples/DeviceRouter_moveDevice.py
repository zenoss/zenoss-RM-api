#!/usr/bin/env python
#####################################################
# This script is a basic example of how to move a   #
# device in Zenoss Resource Manager using the       #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################
#
# SMA
# Does not work, no DeviceRouter method 'moveDevice'.
# There is 'moveDevices', but requires diff parameters to be passed.
#

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'DeviceRouter'
method = 'moveDevice'

usage = '%s <device_id> <device_class_name>' % (sys.argv[0])


def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)


def buildArgs():
    '''
    This builds the data dictionary required for the API call. We check to
    make sure we have exactly the correct arguments, then return the dict
    '''
    if len(sys.argv) != 3:
        fail()
    else:
        try:
            device = sys.argv[1]
            deviceClass = sys.argv[2]
        except:
            fail()
    data = {'deviceName': device,
            'deviceClass': deviceClass}
    return data


def moveDevice(data):
    '''
    This makes the API call and returns the result
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    api_response = moveDevice(data)
    print data
    print api_response
