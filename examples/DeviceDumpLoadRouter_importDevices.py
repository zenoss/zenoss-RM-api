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
    parser.add_argument('-o', dest='inFileName', action='store', default=None,
                        required=True, help="File to read for zenbatch devices")
                        
    return parser.parse_args()

if __name__ == '__main__':
    args = vars(buildArgs())
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    api = zenApiLib.zenConnector(
        routerName = 'DeviceDumpLoadRouter',
        cfgFilePath=args['configFilePath'],
        section=args['configSection'],
        loglevel=args['loglevel']
    )
    api.config['timeout'] = 600 # Override API timeout, zen batch dump can take a long time to return data 

    fp = open(args['inFileName'])
    apiResult = api.callMethod(
                    'importDevices',
                    data=fp.read())
    fp.close()
    if apiResult['result']['success']:
        print >>sys.stderr, "Import successful, import stats: {}".format(
            apiResult['result']['stats']
        )
    else:
        print >>sys.stderr, "ERROR: API results nonsuccessfull\n{}".format(
            pformat(apiResult))
