#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add a    #
# device into Zenoss Resource Manager using the     #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'ManufacturersRouter'
method = 'addNewProduct'

usage = '%s <prodKeys> <prodName> <type> <uid>' % (sys.argv[0])


def fail():
    print 'Invalid arguments. \nUsage: %s' % (usage)
    sys.exit(1)


def buildArgs():
    '''
    This builds the data dictionary required for the API call. We check to
    make sure we have exactly the correct arguments, then return the dict
    '''
    if len(sys.argv) != 5:
        fail()
    else:
        try:
            prodKeys = sys.argv[1]
            prodName = sys.argv[2]
            type = sys.argv[3]
            uid = sys.argv[4]
        except:
            fail()
    params = {
            'uid': uid,
            'prodkeys': prodKeys,
            'prodname': prodName,
            'type': type,
            'partno': '',
            'description': '',
            'oldname': ''}
    data = {'params': params}
    return data


def addNewProduct(data):
    '''
    This makes the API call and returns the result
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    api_response = addNewProduct(data)
    print api_response
