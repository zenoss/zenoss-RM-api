#!/usr/bin/env python
#####################################################
# This script is a basic example of how to add an   #
# OS Process Definition into Zenoss Resource Manager#
# using the Zenoss JSON API and ZenAPILib           #
# in this example we use a text file where each     #
# line contains a new process.  This was done so    #
# the script could be re-used without modifying it  #
#####################################################

# stdlib Imports
import json
from sys import exit
import os
from urlparse import urlparse
import zenApiLib

PROCESS_ROOT= '/zport/dmd/Processes/osProcessClasses'

def addProcessFromFile():
    '''
    This makes the API call and returns data
    '''
    processRouter = zenApiLib.zenConnector(routerName='ProcessRouter')
    file = open("Processlist.txt", "r")
    for process in file:
        processRouter.callMethod('addNode', type="class", id=process.strip(), contextUid="/zport/dmd/Processes")
        processRouter.callMethod('setInfo', uid=(PROCESS_ROOT + '/' + process.strip()), includeRegex=('^[^ ]*' + process.strip() + '[^ /]*( |$)'))

if __name__ == '__main__':
    addProcessFromFile()
