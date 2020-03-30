#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add a    #
# device into Zenoss Resource Manager using the     #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

import sys
import zenApiLib

router = 'CMDBIntegrationNGRouter'
method = 'getCiObject'

usage = '%s <device_id> <device_class_name> <productionState>' % (sys.argv[0])


def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)


def buildArgs():
    '''
    This builds the data dictionary required for the API call. We check to
    make sure we have exactly the correct arguments, then return the dict
    '''
    if len(sys.argv) != 2:
        fail()
    else:
        try:
            ciid = sys.argv[1]
        except:
            fail()
    data = {'ciid': ciid}
    return data


def addDevice(data):
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
    api_response = addDevice(data)
    print api_response
