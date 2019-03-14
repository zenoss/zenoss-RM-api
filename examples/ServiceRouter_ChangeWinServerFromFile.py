#!/usr/bin/env python
#####################################################
# This script is a basic example of how to change   #
# attributes of a Windows Service Definition        #
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

SERVICE_ROOT= '/zport/dmd/Services/WinService/serviceclasses'

def setWinServiceMonitored():
    '''
    This makes the API call and returns data
    '''
    serviceRouter = zenApiLib.zenConnector(routerName='ServiceRouter')
    file = open("servicelist.txt", "r")
    for service in file:
        serviceRouter.callMethod('setInfo', uid=(SERVICE_ROOT + '/' + service.strip()), zMonitor={"isAcquired": False, "localValue": True}, monitoredStartModes='Manual')

if __name__ == '__main__':
    setWinServiceMonitored()
   
