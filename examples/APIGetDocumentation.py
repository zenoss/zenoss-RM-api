#!/bin/env python
import zenApiLib
import argparse
import sys
import logging

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
    parser.add_argument('-i', dest='rnm', action='append',  default=[],
                        metavar="routerName.methodName", required=True, help='API '
                        "router & method name separated by a period. '*' can "
                        "be used as a wildcard, ex: 'DeviceRouter.*'")
    parser.add_argument('-s', dest='silent', action='store_true',
                        help="Silence missing router/method messages")
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    args = vars(buildArgs())
    logging.getLogger().setLevel(args['loglevel'])
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
    for rnm in args['rnm']:
        arName, amName = rnm.split(".")
        if arName == "*":
            rName = sorted(api._routersInfo.keys())
        else:
            rName = [arName]
        for apiRouterName in rName:
            try:
                api.setRouter(apiRouterName)
            except Exception as e:
                if not args['silent']:
                    print e
                continue
            if amName == "*":
                mName = api._routersInfo[apiRouterName]['methods'].keys()
            else:
                mName = [amName]
            for apiMethodName in mName:
                if apiMethodName not in api._routersInfo[apiRouterName]['methods'].keys():
                    if not args['silent']:
                        print "Specified router method '%s' is not an option. Available methods for '%s' router are: %s" % (
                            apiMethodName,
                            apiRouterName,
                            sorted(api._routersInfo[apiRouterName]['methods'].keys())
                        )
                    continue
                mInfo = api._routersInfo[apiRouterName]['methods'][apiMethodName]
                print >>rOut, (
                    "ROUTER NAME: {}\n"
                    "METHOD NAME: {}\n"
                    "METHOD DOCUMENTATION: {}\n"
                    "METHOD ARGS: {}\n"
                    "METHOD KWARGS: {}\n"
                    "---------------------------------------".format(
                        apiRouterName,
                        apiMethodName,
                        str(mInfo['documentation']).replace('\n', '\n\t'),
                        mInfo['args'],
                        mInfo['kwargs']
                    )
                )
        if len(rName) > 1:
            print '======================================'
