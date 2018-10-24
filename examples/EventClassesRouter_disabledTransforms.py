#!/bin/env python

import zenApiLib
import sys
from pprint import pprint

def transformEnabled(evtUid):
    '''
    API caller with simple error check
    '''
    rsp = api.callMethod('isTransformEnabled', uid=evtUid)
    if rsp.get('result', {}).get('success', False) == False:
        print "ERROR"
        pprint(rsp)
        sys.exit(1)
    return  rsp.get('result', {}).get('data', 'Unknown')

def getMappings(evtUid):
    '''
    API caller with simple error check
    '''
    rsp = api.callMethod('getInstances', uid=evtUid)
    if rsp.get('result', {}).get('success', False) == False:
        print "ERROR"
        pprint(rsp)
        sys.exit(1)
    return  rsp.get('result', {}).get('data', [])

def mappings(evtClsUid='/zport/dmd/Events'):
    '''
    Recursively get the mapping from event class uid (evtClsUid).
    Will mapping transform.
    '''
    #EventClassesRouter-getInstances is recursive, grabbing all mappings found under it
    for mapping in getMappings(evtClsUid):
        if mapping.get('hasTransform', False):
            if not transformEnabled(mapping['uid']):
                mappingPath = mapping.get('uid', 'Unknown').replace('/zport/dmd/', '').replace('/instances/', '/')
                print 'Mapping {} transform DISABLED'.format(mappingPath)

def check4transform(evtCls):
    '''
    Logic check, if true will print transform data
    '''
    if evtCls.get("text", {}).get("hasTransform", False):
        if not transformEnabled(evtCls['uid']):
            print 'EventClass {} transform DISABLED'.format(evtCls['path'])

def eventClasses(evtClsUid):
    '''
    Recursively get the event classes from event class uid (evtClsUid).
    API caller, without error check since 'success' field not returned.
    Will print event class transform.
    '''
    rsp = api.callMethod('asyncGetTree', id=evtClsUid)
    evtClsTree = rsp.get('result', [])
    for evtCls in evtClsTree:
        #
        check4transform(evtCls)
        #
        if evtCls['leaf'] ==  False:
            #Strangely some 'branches' (not a leaf) have children defined 
            #while some do not, but have count > 0. Hence the logic below.
            if evtCls.get('children', []):
                for evtClsChidren in evtCls.get('children', []):
                    check4transform(evtClsChidren)
                    eventClasses(evtClsChidren['uid'])
            elif evtCls.get("text", {}).get("count", 0):
                eventClasses(evtCls['uid'])

if __name__ == '__main__':
    api = zenApiLib.zenConnector(routerName = 'EventClassesRouter')
    api.config['timeout'] = 30
    mappings('/zport/dmd/Events')
    eventClasses('/zport/dmd/Events')
