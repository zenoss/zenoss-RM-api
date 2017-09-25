#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of devices and display device-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'DashboardRouter'
method = 'getDeviceIssues'
data = {}

def getDeviceIssues():
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data

def deviceIssuesReport():
    report_data = getDeviceIssues()['data']
    print 'Device, Device Class, ProdState, Clear, Debug, Info '\
          'Warning, Error, Critical'
    for entry in report_data:
        device = entry['device']
        deviceClass = entry['deviceClass']['uid'].replace('/zport/dmd/Devices', '')
        prodState = entry['productionStateLabel']
        events = entry['events']
        clear = events['clear']['count']
        debug = events['debug']['count']
        info = events['info']['count']
        warning = events['warning']['count']
        error = events['error']['count']
        critical = events['critical']['count']
        print '%s, %s, %s, %s, %s, %s, %s, %s, %s' % (device, 
                                                      deviceClass,
                                                      prodState, 
                                                      clear, 
                                                      debug, 
                                                      info, 
                                                      warning, 
                                                      error, 
                                                      critical)

if __name__ == '__main__':
    blah = deviceIssuesReport()
