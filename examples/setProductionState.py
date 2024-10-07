#!/usr/bin/env python
#####################################################
# Copyright (C) Zenoss, Inc. 2024, all rights reserved.
# Author: Team Pinecone
# Contact: Bill Loss 'closs  @ zenoss.com'
#####################################################

from __future__ import print_function

import sys
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder

router = 'DeviceRouter'
method = 'setProductionState'

usage = '%s <device_id> <device_class_name>' % (sys.argv[0])


def fail():
    print('Invalid arguments. \nUsage: %s' % (usage))
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
            prodStateNumber = sys.argv[2]
        except:
            fail()
    data = {'deviceName': device,
            'prodState': prodStateNumber
           }
    return data


def setProdState(**data):
    '''
    This makes the API call and returns the result
    '''
    dr = zenApiLib.zenConnector(routerName = router)
    response = dr.callMethod(method, **data)
    #response = dr.callMethod(method, override=data)
    if response.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % response)
    return response['result']


if __name__ == '__main__':
    '''
    Build the args and make the API call to set the device production state
    '''
    data = buildArgs()
    print(data)
    deviceFindResults = ZenDeviceUidFinder(name=data['deviceName'])
    if deviceFindResults.getCount() > 1:
        raise Exception('Multiple devices found that matched "%s"' % data['deviceName'])
    data['uid'] = deviceFindResults.getFirstUid()
    #import pdb; pdb.set_trace()
    api_response = setProdState(uids=data['uid'], prodState=data['prodState'], hashcheck=0)
    print(data)
    print(api_response)
