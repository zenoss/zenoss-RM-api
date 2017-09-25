#!/usr/bin/env python
#####################################################
# This script is a basic example of how to retrieve #
# a list of routers and display their methods and   #
# associated documentation using the Zenoss JSON    #
# API and the ZenAPIConnector class written by Adam #
# McCurdy @ Zenoss                                  #
#####################################################

import sys
from ZenAPIConnector import ZenAPIConnector

router = 'IntrospectionRouter'


def getAllRouters():
    method = 'getAllRouters'
    data = {}
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    data = response.json()['result']['data']
    routers = {}
    for r in data:
        routers[r['action']] = r['urlpath']
    print routers
    return routers


def getAllRouterMethods():
    all_routers = getAllRouters()
    method = 'getRouterMethods'
    router_methods = {}
    for router_name in all_routers.keys():
        data = {'router': router_name}
        api = ZenAPIConnector(router, method, data)
        response = api.send()
        sys.stdout.write('.')
        sys.stdout.flush()
        data = response.json()
        router_methods[router_name] = data
    return router_methods


def printInfo(router_methods):
    for k, v in router_methods.iteritems():
        methods = v['result']['data']
        for method, info in methods.iteritems():
            print 'ROUTER NAME: %s' % (k)
            print 'METHOD: %s' % (method)
            print 'METHOD DOCUMENTATION: %s' % info['documentation']
            print 'METHOD ARGS: %s' % info['args']
            print 'METHOD KWARGS: %s' % info['kwargs']
            print '---------------------------------------'
        print '======================================'

if __name__ == '__main__':
    router_methods = getAllRouterMethods()
    printInfo(router_methods)
