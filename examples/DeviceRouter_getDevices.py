#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of devices and display device-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

import zenApiLib

router = 'DeviceRouter'
method = 'getDevices'
data = {'limit': 200, 'keys': ['name', 'ipAddressString', 'uid', 'productionState', 'collector']}


def deviceReport():
    ''''
    This sorts through the data and displays results in a
    .csv format. There are numerous other fields that can
    be displayed here, but here are a few as an example.
    '''
    print('Name, IP Address, UID, ProdState, Collector, Location')
    dr = zenApiLib.zenConnector(routerName = router)
    for device_resp in dr.pagingMethodCall(method, **data):
        if device_resp.get('result', {}).get('success', False) is False:
            raise Exception('API call returned unsucessful result.\n%s' % device_resp)
        for dev in device_resp['result']['devices']:
            try:
                location = dev['location']['uid']
            except (KeyError, TypeError):
                location = ''
            print('%s, %s, %s, %s, %s, %s' % (dev['name'],
                                              dev['ipAddressString'],
                                              dev['uid'],
                                              dev['productionState'],
                                              dev['collector'],
                                              location))


if __name__ == '__main__':
    deviceReport()
