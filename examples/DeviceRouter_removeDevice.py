#!/usr/bin/env python
#####################################################
# This script is a basic example of how to remove a   #
# device into Zenoss Resource Manager using the     #
# Zenoss JSON API and the Zenoss RM API Library    #
#####################################################


import sys
import logging
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder



device_id = sys.argv[1]

response = ZenDeviceUidFinder(name=device_id)

if response.getCount() == 1:
    device_uid = response.getFirstUid()
else:
    print 'Found %s devices.' % (response.getCount())
    sys.exit(1)

dr = zenApiLib.zenConnector(routerName = 'DeviceRouter')

delete_response = dr.callMethod('removeDevices', uids=device_uid, hashcheck="", action="delete")

if delete_response['result']['success'] == True:
    print 'Successfully deleted device: %s' % (device_uid)
