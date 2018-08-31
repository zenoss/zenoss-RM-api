#!/usr/bin/env python
#####################################################
# This script is a basic example of how to reset IP #
# addresses and remodel devices based on a device   #
# organizer using the JSON API and zenAPILib        #
#####################################################

import zenApiLib

deviceRouter = zenApiLib.zenConnector(routerName='DeviceRouter')
uid = '/zport/dmd/Groups/Testers'
method = 'resetIp'
remodelMethod = 'remodel'

def getDevices():
    '''
    This makes the API call and returns data
    '''
    response = deviceRouter.callMethod('getDevices', uid=uid)
    resp_data = response['result']
    return resp_data

def resetIPAndRemodel():
     device_resp = getDevices()
     devlist = [dev['uid'] for dev in device_resp['devices']]
     for dev in devlist:
         deviceRouter.callMethod('resetIp', uids=dev)
         deviceRouter.callMethod('remodel', deviceUid=dev)
         print "Resetting IP and Remodeling %s" % dev

if __name__ == '__main__':
    resetIPAndRemodel()
