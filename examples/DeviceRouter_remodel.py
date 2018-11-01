#!/bin/env python
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder
from zenJobsRouterHelper import watchStatus
import argparse
import sys
from pprint import pprint

def buildArgs():
    parser = argparse.ArgumentParser(description='Remodel Device')
    parser.add_argument('-d', dest='deviceNames', action='append',  default=[],
                        required=True, help="Device name. Specify multiple "
                        "times to spawn remodels for more than one device.")
    parser.add_argument('-p', dest='modelerPlugins', action='store', default='',
                        help="Override default modeler plugins to use. "
                        "Takes a regular expression.")
    parser.add_argument('-s', dest='mPluginCheck', action='store_true',
                        help="Do not check if '-p' are valid plugin names. "
                        "Useful when using a complex regular expression.")
    parser.add_argument('-w', dest='wait', action='store_true',
                        help="Wait on remodel job(s) to exit script.")
    return parser.parse_args()

if __name__ == '__main__':
    args = vars(buildArgs())
    api = zenApiLib.zenConnector()
    api.setRouter('DeviceRouter')
    jobIds = []
    # Check that specified modelerPlugins are valid
    if args['modelerPlugins']:
        apiResult = api.callMethod("getModelerPluginDocStrings", uid="/zport/dmd/Devices")
        try:
            validModelerPlugins = sorted(apiResult['result']['data'].keys())
        except Exception as e:
            print "Error getting modelerPlugins!"
            pprint(apiResult)
            print e
            sys.exit(1)
        for mPlugin in args['modelerPlugins'].split("|"):
            if mPlugin not in validModelerPlugins:
                print "Specified modelerPlugin '{}' is not an option. " \
                      "Available plugins are: {}".format(
                        mPlugin,
                        validModelerPlugins
                      )
                sys.exit(2)
    # Loop over specified devices
    for devName in args['deviceNames']:
        results = ZenDeviceUidFinder(name=devName)
        if results.getCount() != 1:
            print 'Skipping "{}", found {} devices.'.format(devName, results.getCount())
            continue
        devUid = results.getFirstUid()
        apiResult = api.callMethod(
            'remodel',
            deviceUid=devUid,
            collectPlugins='"{}"'.format(args['modelerPlugins']),
            background=True
        )
        if not apiResult['result']['success']:
            print 'Remodeling API cal failed'
            pprint(apiResult)
            continue
        else:
            print "{} - {}".format(devName, apiResult['result']['jobId'])
            jobIds.append([devName, apiResult['result']['jobId']])
    # Hold off exiting the script
    if args['wait']:
        print "Waiting on remodel jobs to complete..."
        for job in jobIds:
            devName, jobId = job
            jobSuccess = watchStatus(jobId)
            if not jobSuccess:
                print "{} remodel job unsuccessful".format(devName)
                break
            print "{} remodel job completed".format(devName)
