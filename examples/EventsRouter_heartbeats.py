#!/bin/env python

import zenApiLib
import sys
from pprint import pprint

def heartbeats(api):
    #data = {'uid': '/zport/dmd', 'page': 1, 'sort': 'severity', 'dir': 'DESC',
    #        'params': {'eventClass': '/Status/Heartbeat', 'lastSeen': '1549558300 TO 1549558600'},
    #        'keys': ['eventState', 'severity', 'device', 'component', 'eventClass', 'summary', 'firstTime', 'lastTime', 'count', 'evid', 'eventClassKey', 'message'],
    #        'limit': 200, 'start': 0}
    data = {
            'keys': [
                     'severity',
                     'device',
                     'component',
                     'summary',
                     'firstTime',
                     'lastTime',
                     'count'
                    ],
            'limit': 200,
            'params': {'eventClass': '/Status/Heartbeat'},
            'start': 0
           }
    rsp = api.callMethod('query', **data)
    if rsp.get('result', {}).get('success', False) == False:
        print "ERROR"
        pprint(rsp)
        sys.exit(1)
    return rsp.get('result', {}).get('events', 'Unknown')


if __name__ == '__main__':
    api = zenApiLib.zenConnector(routerName = 'EventsRouter')
    pprint(heartbeats(api))
