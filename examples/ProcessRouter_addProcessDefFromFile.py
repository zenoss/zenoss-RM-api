#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add an   #
# OS Process Definition into Zenoss Resource Manager#
# using the Zenoss JSON API and ZenAPILib           #
# in this example we use a text file where each     #
# line contains a new process.  This was done so    #
# the script could be re-used without modifying it  #
# If the text file line contains 2 words separated  #
# by white space, the first work will be considered #
# a ProcessOrganizer path, which will be created and#
# the ProcessClass will be placed in                #
#####################################################

#########################
# example text file
#########################
'''
myprocess
myapplication firstAppProcess
myapplication secondAppProcess
mySuite/anotherapp suiteProc
'''

# stdlib Imports
import json
from sys import exit
import os
from urlparse import urlparse
import zenApiLib

PROCESS_ROOT= '/zport/dmd/Processes'
PROCESS_CLASS_ROOT= '/zport/dmd/Processes/osProcesses'

def addProcessFromFile():
    '''
    This makes the API call and returns data
    '''
    processRouter = zenApiLib.zenConnector(routerName='ProcessRouter')
    file = open("Processlist.txt", "r")
    for line in file:
        words = line.strip().split()
        if len(words) == 2:
            (org, process) = words
            myroot = "/".join((PROCESS_ROOT, org, 'osProcessClasses'))
            path = ''
            for node in org.split('/'):
                processRouter.callMethod('addNode', type="oroganizer", id=node, contextUid=PROCESS_ROOT+path)
                path = '/'.join((path, node))
        else:
            process = words[0]
            myroot = PROCESS_CLASS_ROOT
        processRouter.callMethod('addNode', type="class", id=process, contextUid=myroot)
        includeRegex = '^[^ ]*{}[^ /]*( |$)'.format(process)
        replaceRegex = '^([^ ]*{}[^ /]*)( |$)'.format(process)
        processRouter.callMethod(
            'setInfo',
            uid="/".join((myroot, process)),
            includeRegex=includeRegex,
            replaceRegex=replaceRegex,
            replacement='\\1'
        )

if __name__ == '__main__':
    addProcessFromFile()
