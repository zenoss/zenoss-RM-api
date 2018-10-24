#!/bin/env python
import zenApiLib
import sys
import os
from urlparse import urlparse
from datetime import date


def write2File(sType, sUid, sData):
    '''
    Write transform text to a file
    '''
    exportPath = '{}/export_{}_{}'.format(
        ".",
        zenInstance,
        date.today()
    )
    if not os.path.exists(exportPath):
        os.makedirs(exportPath)
    sFilePath = "{}/{}.{}.txt".format(
        exportPath,
        sUid,
        sType
    )
    print "INFO: writing {}".format(
        sFilePath
    )
    try:
        oFile = open(sFilePath, 'w')
        oFile.write(sData)
        oFile.close()
    except Exception, e:
        print "ERROR: %s" % (e)
        sys.exit(1)


if __name__ == '__main__':
    api = zenApiLib.zenConnector(routerName = 'EventClassesRouter')
    api.config['timeout'] = 600 # Override API timeout, zen batch dump can take a long time to return data 
    zenInstance = urlparse(api.config['url']).hostname
    api.setRouter('DeviceDumpLoadRouter')
    apiResult = api.callMethod('exportDevices', deviceClass="/Devices/")
    if apiResult['result']['success']:
        write2File('devices', 'batchDump', apiResult['result']['data'])
