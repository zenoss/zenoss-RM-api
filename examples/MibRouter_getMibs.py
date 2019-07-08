#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of mibs and display mib-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

from ZenAPIConnector import ZenAPIConnector

router = 'MibRouter'
method = 'getOrganizerTree'
data = {"id":"/zport/dmd/Mibs"}

def getMibs():
    '''
    This makes the API call and returns data
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


def mibReport():
    ''''
    This sorts through the data and displays results in a
    .csv format. There are numerous other fields that can
    be displayed here, but here are a few as an example.
    '''
    mib_resp = getMibs()
    mibs = mib_resp
    for mib in mibs[0]['children']:
        try:
            if int(mib['text']['count']) > 0:
                print '%s' % mib['path']
        except:
            print '%s' % mib['uid']

        for child in mib['children']:
            print"  %s" % child['uid']

if __name__ == '__main__':
    mibReport()
