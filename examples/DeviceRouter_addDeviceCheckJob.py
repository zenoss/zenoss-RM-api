#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add a    #
# device into Zenoss Resource Manager using the     #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector, ZenJobsWatcher


router = 'DeviceRouter'
method = 'addDevice'

usage = '%s <device_id> <device_class_name> <productionState>' % (sys.argv[0])


def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)


def buildArgs():
    '''
    This builds the data dictionary required for the API call. We check to
    make sure we have exactly the correct arguments, then return the dict
    '''
    if len(sys.argv) != 4:
        fail()
    else:
        try:
            device = sys.argv[1]
            deviceClass = sys.argv[2]
            productionState = sys.argv[3]
        except:
            fail()
    data = {'deviceName': device,
            'deviceClass': deviceClass,
            'productionState': productionState}
    return data


def addDevice(data):
    '''
    This makes the API call and returns the result
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data['new_jobs'][0]['uuid']


if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    api_response = addDevice(data)
    print 'Created job %s... watching job status' % (api_response)
    zjw = ZenJobsWatcher()
    jobstatus = zjw.watchStatus(api_response, 300)
    print 'Job status %s, Success: %s' % (jobstatus[0], jobstatus[1])
