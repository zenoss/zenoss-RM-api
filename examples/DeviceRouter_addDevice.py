#!/usr/bin/env python
import sys
import zenApiLib

router = 'DeviceRouter'
method = 'addDevice'

usage = '%s <device_id> <device_class_name> <productionState> <collector>' % (sys.argv[0])


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
            device = sys.argv[1]
            deviceClass = sys.argv[2]
            productionState = sys.argv[3]
            collector = sys.argv[4]
        except:
            fail()
    data = {'deviceName': device,
            'deviceClass': deviceClass,
            'productionState': productionState,
            'collector': collector}
    return data


def addDevice(data):
    '''
    This makes the API call and returns the result
    '''
    dr = zenApiLib.zenConnector(routerName = router)
    response = dr.callMethod(method, **data)
    if response.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % response)
    return response['result']


if __name__ == '__main__':
    '''
    Build the args and make the API call to add the device
    '''
    data = buildArgs()
    api_response = addDevice(data)
    print api_response
