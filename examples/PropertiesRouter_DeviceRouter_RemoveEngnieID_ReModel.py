#!/usr/bin/env python
################################################################
# This was written by Adam McCurdy during GalaxZ18 as an       #
# example of how to remove a local zProperty (zSnmpEngineId)   #
# and re-model a device to handle a specific customer          #
# use-case.                                                    #
################################################################
import sys
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder

device_id = sys.argv[1]

response = ZenDeviceUidFinder(name=device_id)

if response.getCount() == 1:
    device_uid = response.getFirstUid()
else:
    print 'Found %s devices.' % (response.getCount())
    sys.exit(1)

pr = zenApiLib.zenConnector(routerName='PropertiesRouter')

delete_response = pr.callMethod('deleteZenProperty',
                                zProperty='zSnmpEngineId',
                                uid=device_uid)

if delete_response['result']['success'] == True:
    print 'Deleted EngineID on %s' % (device_uid)
else:
    print 'Unable to delete EngineID on %s' % (device_uid)
    sys.exit(1)

dr = zenApiLib.zenConnector(routerName='DeviceRouter')

remodel_response = dr.callMethod('remodel', deviceUid=device_uid)

if remodel_response['result']['success'] == True:
    print 'Model job submitted.'
