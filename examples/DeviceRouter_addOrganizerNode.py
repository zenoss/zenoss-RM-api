#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add a    #
# location into Zenoss Resource Manager using the   #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'DeviceRouter'
method = 'addNode'

usage = '%s <new_node>'  % (sys.argv[0])


def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)


def buildArgs():
    '''
    This builds the data dictionary required for the API call. We check to
    make sure we have exactly the correct arguments, then return the dict
    '''
    if len(sys.argv) != 2:
        fail()
    else:
        try:
            contextUid, node = sys.argv[1].rsplit('/', 1)
        except:
            fail()
    data = {'id': node,
            'description': '',
            'type': 'organizer',
            'contextUid': contextUid}
    return data


def addNode(data):
    '''
    This makes the API call and returns the result
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data

def recursePath(data):
    '''
    A KeyError means that part of our path didn't exist.
    We step backwards to find it and build the path.
    '''
    orgs = data.split('/')
    newOrgs = orgs[4:]

    count = 0
    buildOrgs = '/zport/dmd/Systems' # 'Systems' could be 'Groups' or 'Devices'
    while count < len(newOrgs):
        buildOrgs += "/" + newOrgs[count]
        count += 1
        contextUid, node = buildOrgs.rsplit('/', 1)
        data = {'id': node,
                'description': '',
                'type': 'organizer',
                'contextUid': contextUid}
        api_response = addNode(data) 
        print api_response

if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    api_response = addNode(data)
    if 'KeyError' in api_response['msg']:
        try:
            recursePath(sys.argv[1])
        except Exception, e:
            print e
    else:
        print api_response
