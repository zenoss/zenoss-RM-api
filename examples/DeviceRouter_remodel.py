#!/bin/env python
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder
from zenApiJobsRouterHelper import watchStatus
import argparse
import sys
import logging
from pprint import pformat

def buildArgs():
    parser = argparse.ArgumentParser(description='Remodel Device')
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
    parser.add_argument('-d', dest='deviceNames', action='append',  default=[],
                        required=True, help="Device name. Specify multiple "
                        "times to spawn remodels for more than one device.")
    parser.add_argument('-m', dest='modelerPlugins', action='store', default='',
                        help="Override default modeler plugins to use. "
                        "Takes a regular expression.")
    parser.add_argument('-s', dest='mPluginCheck', action='store_true',
                        help="Do not check if '-p' are valid plugin names. "
                        "Useful when using a complex regular expression.")
    parser.add_argument('-w', dest='wait', action='store_true',
                        help="Wait on remodel job(s) to exit script.")
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
    api.setRouter('DeviceRouter')
    jobIds = []
    # Check that specified modelerPlugins are valid
    if args['modelerPlugins']:
        apiResult = api.callMethod("getModelerPluginDocStrings", uid="/zport/dmd/Devices")
        try:
            validModelerPlugins = sorted(apiResult['result']['data'].keys())
        except Exception as e:
            print >> sys.stderr, "ERROR getting modelerPlugins!"
            print >> sys.stderr, pformat(apiResult)
            print >> sys.stderr, e
            sys.exit(1)
        for mPlugin in args['modelerPlugins'].split("|"):
            if mPlugin not in validModelerPlugins:
                print >> sys.stderr, "ERROR: Specified modelerPlugin '{}' is not an option. " \
                      "Available plugins are: {}".format(
                        mPlugin,
                        validModelerPlugins
                      )
                sys.exit(2)
    # Loop over specified devices
    for devName in args['deviceNames']:
        results = ZenDeviceUidFinder(name=devName)
        if results.getCount() != 1:
            print >> sys.stderr, 'Skipping "{}", found {} devices.'.format(devName, results.getCount())
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
            print >> rOut, "{} - {}".format(devName, apiResult['result']['jobId'])
            jobIds.append([devName, apiResult['result']['jobId']])
    # Hold off exiting the script
    if args['wait']:
        print >> rOut, "Waiting on remodel jobs to complete..."
        for job in jobIds:
            devName, jobId = job
            jobSuccess = watchStatus(jobId)
            if not jobSuccess:
                print >> rOut, "{} remodel job unsuccessful".format(devName)
                break
            print >> rOut, "{} remodel job completed".format(devName)
