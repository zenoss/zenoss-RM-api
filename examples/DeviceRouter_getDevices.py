#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of devices and display device-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

from ZenAPIConnector import ZenAPIConnector

router = 'DeviceRouter'
method = 'getDevices'
data = {'limit': 200}


def getDevices():
    '''
    This makes the API call and returns data
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


def deviceReport():
    ''''
    This sorts through the data and displays results in a
    .csv format. There are numerous other fields that can
    be displayed here, but here are a few as an example.
    '''
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
