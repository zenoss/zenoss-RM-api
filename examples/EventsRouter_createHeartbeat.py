#!/bin/env python

# Create heartbeat events based on kb Article
# https://support.zenoss.com/hc/en-us/articles/203048445-How-To-Send-Heartbeat-Events-From-Applications

from __future__ import print_function

import zenApiLib
import sys
from pprint import pprint


def heartbeats(api):
    data = {
                'summary': 'Hearbeat',
                'device': 'mydevicename',
                'component': '',
                'severity': 5,
                'evclass': '/Heartbeat',
                'evclasskey': '',
                'message': 'test',
                'timeout': 300   #time in seconds before creating the heartbeat event
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
