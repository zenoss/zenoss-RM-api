#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of devices and display device-related info   #
# using the Zenoss JSON API and the ZenAPIConnector #
# class written by Adam McCurdy @ Zenoss            #
#####################################################
from __future__ import print_function

import zenApiLib

router = 'PropertiesRouter'
method = 'getZenProperties'
data = {'uid': '/zport/dmd/Devices/Server/Linux'}

def getProperties():
    '''
    This makes the API call and returns data
    '''
    dr = zenApiLib.zenConnector(routerName = router)
    response = dr.callMethod(method, **data)
    if response.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % response)
    return response['result']


def printProperties(response):
    my_data = response['data']
    for prop in my_data:
        id = prop['id']
        category = prop['category']
        label = prop['label']
        isLocal = prop['islocal']
        value = prop['value']
        description = prop['description']
        print('%s,,%s,,%s,,%s,,%s,,%s' % (id,
                                          category,
                                          label,
                                          isLocal,
                                          value,
                                          description))

if __name__ == '__main__':
    response = getProperties()
    print('ID,,Category,,Label,,IsLocal?,,Value,,Description')
    printProperties(response)
