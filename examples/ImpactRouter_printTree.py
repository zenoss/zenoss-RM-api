#!/usr/bin/env python

from zenApiImpactRouterHelper import (
    zenApiImpactRouterHelper,
    IMPACT_ROOT
)

api = zenApiImpactRouterHelper()

def printTree():
    print "\nDisplaying tree of all services and organizers...\n"
    print "GUID                                 UID"
    print "---------------------------------    ---------------------"
    tree = api.get_services_tree()
    _printTreeRecursive(tree)

def _printTreeRecursive(tree):
    print tree['uuid'], tree['path']
    for child in tree['children']:
       _printTreeRecursive(child)

if __name__ == '__main__':
    printTree()
