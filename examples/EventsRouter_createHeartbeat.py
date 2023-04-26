#!/bin/env python
from __future__ import print_function

import zenApiLib
import sys
from pprint import pprint

def heartbeats(api):
    data = {
                'summary': 'Hearbeat',
                'device': 'bryantest',
                'component': '',
                'severity': 5,
                'evclass': '/Heartbeat',
                'evclasskey': 'none',
                'message': 'test',
                'monitor': 'AustinCollectorPool',
                'timeout': 120
           }
    rsp = api.callMethod('add_event', **data)
    if rsp.get('result', {}).get('success', False) == False:
        print("ERROR")
        pprint(rsp)
        sys.exit(1)
    return rsp.get('result', {}).get('success', 'Unknown')


if __name__ == '__main__':
    api = zenApiLib.zenConnector(routerName = 'EventsRouter')
    pprint(heartbeats(api))
