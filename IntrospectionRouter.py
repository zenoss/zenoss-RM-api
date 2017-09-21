#!/usr/bin/env python
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
