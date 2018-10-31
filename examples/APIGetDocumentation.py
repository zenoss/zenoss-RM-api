#!/bin/env python
import zenApiLib
import argparse

def buildArgs():
    parser = argparse.ArgumentParser(description='Poll & display API Router & '
                        'Method information. Wildcards can be used to "search"'
                        ' for methodNames across routers.')
    parser.add_argument('-i', dest='rnm', action='append',  default=[],
                        metavar="routerName.methodName", required=True, help='API '
                        "router & method name separated by a period. '*' can "
                        "be used as a wildcard, ex: 'DeviceRouter.*'")
    parser.add_argument('-s', dest='silent', action='store_true',
                        help="Silence missing router/method messages")
    return parser.parse_args()

if __name__ == '__main__':
    args = vars(buildArgs())
    api = zenApiLib.zenConnector()
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
                #pprint(api._routersInfo[apiRouterName]['methods'][apiMethodName])
                mInfo = api._routersInfo[apiRouterName]['methods'][apiMethodName]
                print (
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