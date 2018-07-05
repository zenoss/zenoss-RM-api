#!/bin/env python

# API version of script found at:
# https://support.zenoss.com/hc/en-us/articles/202423289-How-To-List-All-Event-Transforms-and-Event-Class-Mappings


import zenApiLib
import sys
from pprint import pprint

def getTransform(evtUid):
    '''
    API caller with simple error check
    '''
    rsp = api.callMethod('getTransform', uid=evtUid)
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
            mappingPath = mapping.get('uid', 'Unknown').replace('/zport/dmd/', '').replace('/instances/', '/')
            label = '[Mapping] %s' % mappingPath
            print '%s\n%s' % (label, '-' * len(label))
            print getTransform(mapping['uid']), "\n"

def check4transform(evtCls):
    '''
    Logic check, if true will print transform data
    '''
    if evtCls.get("text", {}).get("hasTransform", False):
        label = '[Transform] %s' % evtCls['path']
        print '%s\n%s' % (label, '-' * len(label))
        print getTransform(evtCls['uid']), "\n"

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
    mappings('/zport/dmd/Events')
    eventClasses('/zport/dmd/Events')
