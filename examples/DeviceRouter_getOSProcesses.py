#!/usr/bin/env python
#######################################################
# This is a report that prints out OS Processes that have 
# been modeled on or added to servers, along with their 
# monitored state             
#######################################################
from __future__ import print_function
import zenApiLib
zenApi = zenApiLib.zenConnector()
zenApi.setRouter('DeviceRouter')
devices = zenApi.callMethod('getDevices', keys='uid')['result']['devices']

# peel out UIDs from the list of devices
device_uids = []
for dev in devices:
    device_uids.append(dev['uid'])

# loop through all devices and make an API call looking for OSProcess components
for device_uid in device_uids:
    getcomp_result = zenApi.callMethod('getComponents', uid=device_uid, meta_type='OSProcess', keys=['name', 'monitored'])['result']
    # if the totalCount is greater than zero, let's print out the device name, component name, and the monitored state
    if getcomp_result['totalCount'] > 0:
        for component in getcomp_result['data']:
            print('%s, %s, %s' % (device_uid, component['name'], component['monitored']))
