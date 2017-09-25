#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create   #
# display dashboard information using the Zenoss    #
# JSON API and the ZenAPIConnector class written by #
# Adam McCurdy @ Zenoss                             #
#####################################################

from ZenAPIConnector import ZenAPIConnector

router = 'DashboardRouter'
method = 'getDeviceIssues'
data = {}


def getDeviceIssues():
    '''
    This method makes the API call and returns the response
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


def deviceIssuesReport():
    '''
    This method sorts through the data and prints it out in
    .csv format. There are several other fields one might be
    interested in here, but here are a few as an example.
    '''
    report_data = getDeviceIssues()['data']
    print 'Device, Device Class, ProdState, Clear, Debug, Info '\
          'Warning, Error, Critical'
    for entry in report_data:
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
    '''
    Run the report
    '''
    deviceIssuesReport()
