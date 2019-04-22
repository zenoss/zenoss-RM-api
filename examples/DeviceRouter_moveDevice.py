#!/usr/bin/env python
#####################################################
# This script is a basic example of how to move a   #
# device in Zenoss Resource Manager using the       #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################
#

import sys
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder

router = 'DeviceRouter'
method = 'moveDevices'

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
            'deviceClass': "/zport/dmd{}".format(deviceClass)}
    return data


def moveDevice(**data):
    '''
    This makes the API call and returns the result
    '''
    dr = zenApiLib.zenConnector(routerName = router)
    response = dr.callMethod(method, **data)
    if response.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % response)
    return response['result']


if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    deviceFindResults = ZenDeviceUidFinder(name=data['deviceName'])
    if deviceFindResults.getCount() > 1:
        raise Exception('Multiple devices found that matched "%s"' % data['deviceName'])
    data['uid'] = deviceFindResults.getFirstUid()
    api_response = moveDevice(uids=data['uid'], target=data['deviceClass'])
    print data
    print api_response
