#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create   #
# display dashboard information using the Zenoss    #
# JSON API and the ZenAPIConnector class written by #
# Adam McCurdy @ Zenoss                             #
#####################################################
from __future__ import print_function
import zenApiLib


def deviceIssuesReport():
    '''
    This method sorts through the data and prints it out in
    .csv format. There are several other fields one might be
    interested in here, but here are a few as an example.
    '''
    print('Device, Device Class, ProdState, Clear, Debug, Info '\
          'Warning, Error, Critical')
    dr = zenApiLib.zenConnector(routerName = 'DashboardRouter')
    report_data = dr.callMethod('getDeviceIssues')
    if report_data.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % report_data)
    for entry in report_data['result']['data']:
        device = entry['device']
        deviceClass = entry['deviceClass']['uid']
        deviceClass = deviceClass.replace('/zport/dmd/Devices', '')
        prodState = entry['productionStateLabel']
        events = entry['events']
        clear = events['clear']['count']
        debug = events['debug']['count']
        info = events['info']['count']
        warning = events['warning']['count']
        error = events['error']['count']
        critical = events['critical']['count']
        print('%s, %s, %s, %s, %s, %s, %s, %s, %s' % (device,
                                                      deviceClass,
                                                      prodState,
                                                      clear,
                                                      debug,
                                                      info,
                                                      warning,
                                                      error,
                                                      critical))


if __name__ == '__main__':
    '''
    Run the report
    '''
    deviceIssuesReport()
