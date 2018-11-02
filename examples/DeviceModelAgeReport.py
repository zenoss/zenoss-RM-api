#!/bin/env python
import zenApiLib
import argparse
import sys
import time
import logging
from pprint import pformat

def buildArgs():
    parser = argparse.ArgumentParser(description='Create a comma delimited report'
                        ' of device model status with other related data.') 
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-c', dest='configSection', action='store',
                        metavar="credsSection", default='default',
                        help='zenApiLib credential configuration section '
                        '(default)')
    parser.add_argument('-o', dest='outFileName', action='store', default=None,
                        help="Output to file instead of stdout.")
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)
    args = vars(buildArgs())
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    if args['outFileName']:
        rOut = open(args['outFileName'], 'w')
    else:
        rOut = sys.stdout
    api = zenApiLib.zenConnector(
                        cfgFilePath=args['configFilePath'],
                        section=args['configSection'],
                        loglevel=args['loglevel'])
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
            print >> sys.stderr, "ERROR: {!r}".format(e)
            print >> sys.stderr, pformat(pagedResults)
            sys.exit(1)
        for event in pagedResults['result']['events']:
            issues[event['device']['text']] = event['summary']
    # Loop through Devices and report on model dates
    print >> rOut, "Device Class, Device ID, Device Title, Last Modeled DateTime, Last Modeled Date, Production State, Model Events, Status Up/Down"
    api.setRouter('DeviceRouter')
    for pagedResults in api.pagingMethodCall('getDevices',
                                             keys=['uid', 'id', 'name', 'status', 'lastCollected', 'productionStateLabel'],
                                             sort='uid', dir='ASC'):
        try:
            if not pagedResults['result']['success']:
                raise Exception(pagedResults['msg'])
        except Exception as e:
            print >> sys.stderr, "ERROR: {!r}".format(e)
            print >> sys.stderr, pformat(pagedResults)
            sys.exit(1)
        for device in pagedResults['result']['devices']:
            print >> rOut, '{},{},{},{},{},{},"{}",{}'.format(
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
