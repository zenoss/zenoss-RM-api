#!/usr/bin/env python

# stdlib Imports
import json
from sys import exit
import os
from urlparse import urlparse
from ZenAPIConnector import ZenAPIConnector

zenInstance = 'unknown'

def TriggerRouter(sMethod, dData={}):
    global zenInstance
    sRouter = 'TriggersRouter'
    api = ZenAPIConnector(sRouter, sMethod, dData)
    response = api.send()
    zenInstance = urlparse(api.url).hostname
    if response == None:
        print "Error"  #todo
        exit(1)
    respData = response.json()
    if not respData['result']['success']:
        print "ERROR: TriggerRouter %s method call non-successful" % sMethod
        print respData
        print "Data submitted was:"
        print response.request.body
        exit(1)
    return respData['result']['data']

def write2File(sType, lData):
    exportPath='./export_%s' % zenInstance
    if not os.path.exists(exportPath):
        os.makedirs(exportPath)
    for dEntry in lData:
        print "INFO: writing %s/%s.%s.json" % (exportPath, dEntry['name'], sType)
        try:
            trigFile=open("%s/%s.%s.json" % (exportPath, dEntry['name'], sType),'w')
            trigFile.write(json.dumps(dEntry))
            trigFile.close()
        except Exception, e:
            print "ERROR: %s" % (e)
            exit(1)

if __name__ == "__main__":
    print "Script started, exporting from %s" % zenInstance
    lTriggers=TriggerRouter('getTriggers')
    print "INFO: got event triggers, total of %s" % str(len(lTriggers))
    write2File('trigger', lTriggers)
    #
    lNotifications=TriggerRouter('getNotifications')
    print "INFO: got event notifications, total of %s" % str(len(lNotifications))
    write2File('notification', lNotifications) 
    #
    lNotifWindows=[]
    for dNotif in lNotifications:
        lWindows=TriggerRouter('getWindows', dData={'uid': dNotif['uid']})
        lNotifWindows=lNotifWindows + lWindows
    print "INFO: got event notifications windows, total of %s" % str(len(lNotifWindows))
    write2File('window', lNotifWindows) 
    print "Script completed"
    
