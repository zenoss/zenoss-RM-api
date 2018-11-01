#!/bin/env python
import zenApiLib
import argparse
import sys
import time
from pprint import pprint

def buildArgs():
    parser = argparse.ArgumentParser(description='Create a comma delimited report'
                        ' of device model status with other related data.') 
    return parser.parse_args()

if __name__ == '__main__':
    args = vars(buildArgs())
    api = zenApiLib.zenConnector()
    # Get active zenmodeler events
    issues = {}
    evtQryParams = {
        'severity': [5,4],
        'eventState': [0,1],
        'agent': 'zenmodeler*'
    }
    api.setRouter('EventsRouter')
    for pagedResults in api.pagingMethodCall('query',
                                             params=evtQryParams,
                                             keys=['device', 'summary']):
        try:
            if not pagedResults['result']['success']:
                raise Exception(pagedResults['msg'])
        except Exception as e:
            print "ERROR: {!r}".format(e)
            pprint(pagedResults)
            sys.exit(1)
        for event in pagedResults['result']['events']:
            issues[event['device']['text']] = event['summary']
    # Loop through Devices and report on model dates
    print "Device Class, Device ID, Device Title, Last Modeled DateTime, Last Modeled Date, Production State, Model Events, Status Up/Down"
    api.setRouter('DeviceRouter')
    for pagedResults in api.pagingMethodCall('getDevices',
                                             keys=['uid', 'id', 'name', 'status', 'lastCollected', 'productionStateLabel'],
                                             sort='uid', dir='ASC'):
        try:
            if not pagedResults['result']['success']:
                raise Exception(pagedResults['msg'])
        except Exception as e:
            print "ERROR: {!r}".format(e)
            pprint(pagedResults)
            sys.exit(1)
        for device in pagedResults['result']['devices']:
            print '{},{},{},{},{},{},"{}",{}'.format(
                '/'.join(device['uid'].split('/')[4:-2]),
                device['id'],
                (device['name'] if device['name'] != device['id'] else ''),
                (device['lastCollected'] if isinstance(device['lastCollected'], (str, unicode)) 
                    else time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(device['lastCollected'])))),
                (device['lastCollected'] if isinstance(device['lastCollected'], (str, unicode)) 
                    else time.strftime('%Y/%m/%d', time.localtime(float(device['lastCollected'])))),
                device['productionStateLabel'],
                issues.get(device['name'], 'No Events'),
                ('UP' if device['status'] else 'DOWN')
            )
