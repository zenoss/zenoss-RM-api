#!/usr/bin/env python
################################################################
# This was written by Adam McCurdy during GalaxZ18 as an       #
# example of how to remove old maintenance windows from a      #
# specific device                                              #
################################################################
import zenApiLib
from time import time

dr = zenApiLib.zenConnector(routerName='DeviceManagementRouter')
response = dr.callMethod('getMaintWindows', uid='/zport/dmd/Devices/Discovered/devices/python_device')

def delete_maint_window(mw_uid, mw_id):
    del_response = dr.callMethod('deleteMaintWindow', uid=mw_uid, id=mw_id)
    return del_response['result']['success']

curr_time = time()

for mwindow in response['result']['data']:
    if mwindow['repeat'] == 'Never':
        time_to_delete = curr_time - 86400
        if mwindow['start'] < time_to_delete:
            del_resp = delete_maint_window(mwindow['uid'], mwindow['id'])
            print del_resp
