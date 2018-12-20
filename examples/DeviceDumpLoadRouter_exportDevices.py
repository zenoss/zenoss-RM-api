#!/bin/env python
import zenApiLib
import argparse
import sys
import logging
import os
from urlparse import urlparse
from datetime import date
from pprint import pformat

def buildArgs():
    parser = argparse.ArgumentParser(description='Poll & display API Router & '
                        'Method information. Wildcards can be used to "search"'
                        ' for methodNames across routers.')
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
    parser.add_argument('-d', dest='deviceClasses', action='append',  default=['/'],
                        help='Device Class to extract from. Parameter can be '
                        "specificed multiple times. Default: '/'")
    parser.add_argument('--noorganizers', dest='exOrg', action='store_false',
                        help="Do not dump organizers.")
    parser.add_argument('--nodevices', dest='exDev', action='store_false',
                        help="Do not dump devices.")
                        
    return parser.parse_args()

if __name__ == '__main__':
    args = vars(buildArgs())
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    if args['outFileName']:
        rOut = open(args['outFileName'], 'w')
    else:
        rOut = sys.stdout
    api = zenApiLib.zenConnector(
        routerName = 'DeviceDumpLoadRouter',
        cfgFilePath=args['configFilePath'],
        section=args['configSection'],
        loglevel=args['loglevel']
    )
    api.config['timeout'] = 600 # Override API timeout, zen batch dump can take a long time to return data 
    # workaround for argparser, 'append' will add to default value instead of overriding
    if len(args['deviceClasses']) > 1:
        ignoreDefault = args['deviceClasses'].pop(0)
    for devClass in args['deviceClasses']:
        # ?Bug? (ZEN-31017) - work-around via multiple api calls
        # -- Get device classes first
        if args['exOrg']:
            print >>rOut, "#### {} extract of classes ####".format(devClass)
            apiResult = api.callMethod(
                'exportDevices',
                options={
                    'root': '/zport/dmd/Devices{}'.format(devClass),
                    'regex': '(?!)'
                }
            )
            if apiResult['result']['success']:
                log.info("Extract Org summary results for '{}': {}".format(
                    devClass,
                    apiResult['result']['deviceCount']
                ))
                print >>rOut, apiResult['result']['data']
            else:
                print >>sys.stderr, "ERROR: API results nonsuccessfull\n{}".format(
                    pformat(apiResult)
                )
        if args['exDev']:
            print >>rOut, "#### {} extract of devices ####".format(devClass)
            # -- now devices, with its deviceClass defined in the moveDevice batchload parameter
            apiResult = api.callMethod(
                'exportDevices',
                options={
                    'root': '/zport/dmd/Devices{}'.format(devClass),
                    'noorganizers': True
                }
            )
            if apiResult['result']['success']:
                log.info("Extract Dev summary results for '{}': {}".format(
                    devClass,
                    apiResult['result']['deviceCount']
                ))
                print >>rOut, apiResult['result']['data']
            else:
                print >>sys.stderr, "ERROR: API results nonsuccessfull\n{}".format(
                    pformat(apiResult)
                )
