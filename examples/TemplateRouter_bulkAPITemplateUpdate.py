#!/usr/bin/env python
#####################################################
# This script is a basic example of how to bulk   #
# modify monitoring templates          #
# using the Zenoss JSON API and ZenAPILib           #
# In this example we throw in a new script into the
# datasource.  This is a pretty quick and dirty method #
#####################################################

# stdlib Imports
import json
from sys import exit
import os
from urlparse import urlparse
import zenApiLib

new_script = """$$fail = $$False; try {
    try {
        $$s = Get-ChildItem "${here/directoryPath}" -ErrorAction Stop;
        }
    catch [System.Management.Automation.ActionPreferenceStopException] {
        throw $$_.exception;
    }
} catch [System.Management.Automation.ItemNotFoundException] {
    echo "Does Not Exist";
    $$fail = $$True;
} catch [UnauthorizedAccessException] {
    echo "Permission Denied";
    $$fail = $$True;
} catch {
    echo "Uncaught Exception: $$($$_.exception.message)";
    $$fail = $$True;
} if ($$fail -ne $$True) {
    $$ci = Get-ChildItem ${here/windowsRecursiveSwitch} "${here/directoryPath}\\\*" ${here/windowsFilterOrIncludeSwitch} "${here/filenameMatch}";
    $$mo = $$ci | Measure-Object -Property length -Sum;
    $$numFiles = $$mo | Select-Object -expandProperty Count;
    if ($$numFiles -gt 0) {
        $$fileSize = $$mo | Select-Object -expandProperty Sum;
        $$now = (Get-Date);
        $$oldestFileAge = ($$now - ($$ci | sort LastWriteTime -Descending | select -last 1 | Select-Object -expandProperty LastWriteTime)).TotalSeconds;
        $$newestFileAge = ($$now - ($$ci | sort LastWriteTime | select -last 1 | Select-Object -expandProperty LastWriteTime)).TotalSeconds;
        "$$numFiles,$$fileSize,$$oldestFileAge,$$newestFileAge";
    } else {
        "0,0,0,0";
    }"""
templateRouter = zenApiLib.zenConnector(routerName='TemplateRouter')
deviceRouter = zenApiLib.zenConnector(routerName='DeviceRouter')

def getDeviceList():
    device_resp = deviceRouter.callMethod('getDeviceUids', uid='/zport/dmd/Devices/Server/Microsoft/Windows')
    deviceList = device_resp['result']['devices']
    return deviceList

def bulkUpdateTemplates():
    deviceList = getDeviceList()
    for dev in deviceList:
       directoryMonitorComponents = deviceRouter.callMethod('getComponents', uid=dev, meta_type="DirectoryMonitor")
       # added a try/except here to account for devices taht didn't have directory monitor components, should be more graceful here. 
       try: 
           dm_components = directoryMonitorComponents['result']['data'][0]['uid']
       except IndexError: 
           print "Skipping because no directory monitor component"
           continue
       datasources = templateRouter.callMethod('getDataSources', uid=(dm_components + "/" + "DirectoryMonitor"))
       change_datasource = datasources['result']['data'][0]['uid']
       templateRouter.callMethod('setInfo', uid=(change_datasource), script=new_script)
       print "Changing %s on %s" % (change_datasource, dev) 
if __name__ == '__main__':
    bulkUpdateTemplates()
