#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of mibs and display mib-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################

# complex use-case:
# IFS=$'\n'  
# for  MIB in $(./examples/MibRouter_getMibs.py | grep zport | sed 's/^  //g')  
# do 
#   ./examples/MibRouter_getOids.py "$MIB" 
# done

from ZenAPIConnector import ZenAPIConnector
import sys

router = 'MibRouter'
method = 'getOidMappings'

try:
    MIB = sys.argv[1]
    data = {"uid":MIB}
except:
    data = {"uid":"/zport/dmd/Mibs/mibs/BRIDGE-MIB"}



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
    mibs = mib_resp['data']
    print 'oid, UID'
    for mib in mibs:
        print '%s, %s' % (mib['oid'],
                               mib['uid'])

if __name__ == '__main__':
    mibReport()
