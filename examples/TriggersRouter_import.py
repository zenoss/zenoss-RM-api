#!/usr/bin/env python

# stdlib Imports
import json
from sys import exit, argv
import os
from urlparse import urlparse
import logging
import zenApiLib


# Global Variables
zenAPI = zenApiLib.zenConnector(section = 'default')
zenAPI.log.setLevel(logging.WARN)
zenInstance = urlparse(zenAPI.config['url']).hostname
# For new system migration, need to be able to lookup user/group uuid update
# import data with appropriate uuid.
# #Under API, Not possible at this time
# #If system has the same user/group uuid, then there should not be an issue
# #setting below to False will use the user info defined in the export files.
# #Otherwise script will not set user/group.
bBlankOutUserInfo = True


def TriggerRouter(sMethod, dData={}):
    zenAPI.setRouter('TriggersRouter')
    respData = zenAPI.callMethod(sMethod, **dData)
    if not respData['result']['success']:
        print "ERROR: TriggerRouter %s method call non-successful" % sMethod
        print respData
        print "Data submitted was:"
        print response.request.body
        exit(1)
    return respData['result']['data']


def _extractContent(lData):
    # extract and return a dictionary from Notification Content value
    # example value of content: "{u'items': [{u'items': [{u'allowBlank': True,"
    dExtract = {}
    for x in lData['items']:
        if 'items' in x:
            for i in x['items']:
                dExtract[i['name']] = i['value']
            return dExtract


def getNameIdx(type):
    # Return dictionary acting as an index. Key: Id
    dTypeId = {
        'trigger': {
            'idProperty': 'uuid',
            'apiTriggerRouter': 'getTriggerList'
        },
        'notification': {
            'idProperty': 'uid',
            'apiTriggerRouter': 'getNotifications'
            }
    }
    if type == 'window':
        # getting an index for windows is more invovled
        return _getWindowNameIdx()
    elif not (type in dTypeId.keys()):
        print "ERROR: Caching %s Name-ID index: no such type" % type
        return {}
    log.debug("Caching Index for %ss" % type)
    lResult = TriggerRouter(dTypeId[type]['apiTriggerRouter'])
    return {k['name']: k[dTypeId[type]['idProperty']] for k in lResult}


def _getWindowNameIdx():
    # WINDOW type specific: Return dictionary acting as an index. Key: Id
    global dNotifsIndex
    dTmpIndex = {}
    type = 'window'
    dTypeId = {
        'window': {
            'idProperty': 'uid',
            'apiTriggerRouter': 'getWindows'
        }
    }
    if len(dNotifsIndex) == 0:
        dNotifsIndex = getNameIdx('notification')
    log.debug("Caching Index for Notification Windows")
    for sWinName in dNotifsIndex.keys():
        lResult = TriggerRouter(
            dTypeId[type]['apiTriggerRouter'],
            dData={'uid': dNotifsIndex[sWinName]}
        )
        dTmpIndex.update(
            {k['name']: k[dTypeId[type]['idProperty']] for k in lResult}
        )
    return dTmpIndex


def getConfigOrCreate(type, data):
    if not (type in "trigger, notification, window"):
        print "ERROR: %s creation: no such type" % type
        return {}
    if ((
            type == 'trigger' and
            not (data['name'] in dTrigsIndex)
        ) or (
            type == 'notification' and
            not (data['name'] in dNotifsIndex)
        ) or (
            type == 'window' and
            not (data['name'] in dWinsIndex)
      )):
        dConfig = _createConfig(type, data)
    else:
        dConfig = _getConfig(type, data)
    return dConfig


def _createConfig(type, data):
    # Create config & return its config
    global dTrigsIndex, dNotifsIndex, dWinsIndex, dImportData
    log.debug("Creating %s with name `%s`" % (
        type, data['name']
    ))
    if type == 'trigger':
        sUuid = TriggerRouter('addTrigger', dData={"newId": data['name']})
        dTrigsIndex[data['name']] = sUuid
        dConfig = _getConfig(type, data)
        # Update import data with new uuid value, or the update will not work.
        dImportData['uuid'] = dTrigsIndex[dImportData['name']]
    elif type == 'notification':
        dConfig = TriggerRouter(
            'addNotification',
            dData={
                'newId': data['id'],
                'action': data['action']
            }
        )
        dNotifsIndex[data['name']] = dConfig['uid']
    elif type == 'window':
        # Windows API calls require Notification uid
        sNotifUid = _getWindowNotifUid(data['uid'])
        dConfig = TriggerRouter(
            'addWindow',
            dData={
                "contextUid": sNotifUid,
                "newId": data['name']
            }
        )
        dWinsIndex[data['name']] = dConfig['uid']
    return dConfig


def _getConfig(type, data, warn=False):
    # return config
    global dImportData
    if type == 'trigger':
        dConfig = TriggerRouter(
            'getTrigger',
            dData={
                'uuid': dTrigsIndex[data['name']]
            }
        )
        # Update import data with new uuid value, or the compare will not work.
        dImportData['uuid'] = dTrigsIndex[dImportData['name']]
    elif type == 'notification':
        # Bug?: getNotification does not included a populated 'subscriptions',
        # just an empty list. Could be only Zenoss 4.2
        # dConfig=TriggerRouter('getNotification', lData=[{'uid':data['uid']}])
        dConfig = {}
        for dNotif in TriggerRouter('getNotifications'):
            if data['uid'] == dNotif['uid']:
                dConfig = dNotif
                break
        if dConfig == {}:
            print "ERROR: Did not find notification config for %s" % (
                data['name']
            )
    elif type == 'window':
        # Windows API calls require Notification uid
        # sNotifUid=_getWindowNotifUid(data['uid'])
        dConfig = TriggerRouter(
            'getWindow',
            dData={
                'uid': data['uid']
            }
        )
    # Special fields that require 'processing'
    dConfig = specialFieldProcessing(dConfig, warn)
    return dConfig


def _getWindowNotifUid(uid):
    # infer notification uid from the window's uid
    return uid[0:uid.find('/windows/')]


def specialFieldProcessing(data, warn=False):
    global dTrigsIndex
    # Process data and fudge it if needed
    # CONTENT: Notification content conversion needed for compare and updates
    # to work
    if 'content' in data:
        data.update(_extractContent(data['content']))
        del data['content']
    # START: Window start value
    # Bug?: Update does not like the start key having values with '/',
    # prefers '-'
    #      But get provides the date with '/'
    if 'start' in data:
        data['start'] = data['start'].replace('/', '-')
    # SUBSCRIPTIONS:
    # #Notifications: 'Fudge' so works with pushing notification update, needs
    # #to be a list of uuids
    # #infer this is a notification, if it has an 'action' field.
    if 'subscriptions' in data and 'action' in data:
        if len(dTrigsIndex) == 0:
            dTrigsIndex = getNameIdx('trigger')
        lNotifSubscriptions = []
        for dSub in data['subscriptions']:
            if dSub['name'] in dTrigsIndex:
                lNotifSubscriptions.append(dTrigsIndex[dSub['name']])
            else:
                if warn:
                    log.info(("Unable to update subscription value, trigger"
                           "'%s' does not exist ?") % (dSub['name']))
        data['subscriptions'] = lNotifSubscriptions
    # #Triggers: is this really needed, since the notification config defines
    # #this ?
    if 'subscriptions' in data and 'rule' in data:
        del data['subscriptions']
    # USERS: see top of script comment
    if bBlankOutUserInfo:
        for userFields in ['users', 'recipients']:
            if userFields in data:
                if warn:
                    log.info(("Import '%s' has been ignored and not set"
                           " per script config") % (userFields))
                del data[userFields]
    # INSPECTOR_TYPE & META_TYPE, values of 'Maintenance Window' (v4) change
    # to 'MaintenanceWindow' (v5)
    for field in ["inspector_type", "meta_type"]:
        if field in data:
            if data[field] == "Maintenance Window":
                data[field] = "MaintenanceWindow"
    # Bug?: getTriggers return more fields than getTrigger: globalRead, etc
    # Not going to remove, only impact is that the configuration always gets
    # applied, due to difference.
    return data


def compareData(dataA, dataB):
    bSame = True
    for key in set(dataA.keys() + dataB.keys()):
        if not (key in dataA) or not (key in dataB):
            bSame = False
            log.debug("%s is present: A:%s B:%s" % (
                key,
                (key in dataA),
                (key in dataB)
            ))
            break
        elif dataA[key] != dataB[key]:
            bSame = False
            log.debug("%s value is different:\nA:%s\nB:%s" % (
                key,
                dataA[key],
                dataB[key]
            ))
            break
    return bSame


def updateZenoss(type, data):
    dApiMethod = {
        'trigger': 'updateTrigger',
        'notification': 'updateNotification',
        'window': 'updateWindow'
    }
    if not compareData(data, dZenConfig):
        log.debug("Updating %s" % type)
        log.info("Configuration Applied")
        TriggerRouter(dApiMethod[type], dData=data)


def diffData(type, data):
    dConfig = _getConfig(type, data)
    for key in dConfig.keys():
        if not (key in data):
            log.warn("Compare fail:\n  importNoKey: %s\n  zenoss conf: %s:%s" % (key, key, dConfig[key]))
        elif not (key in dConfig):
            log.warn("Compare fail:\n  import file: %s:%s\n  zenossNoKey: %s" % (key, (key in data),key))
        elif data[key] != dConfig[key]:
            log.warn("Compare fail:\n  import file: %s:%s\n  zenoss conf: %s:%s" % (key, data[key], key, dConfig[key]))

            
def log2stdout(loglevel):
    '''
    Setup logging
    '''
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(loglevel)
    return logging.getLogger('importTriggersNotifications')


dTrigsIndex = {}
dNotifsIndex = {}
dWinsIndex = {}
lTriggers = []
lNotifications = []
lWindows = []
if __name__ == "__main__":
    log = log2stdout(logging.INFO)
    log.info("Script started, importing to %s" % zenInstance)
    argv.pop(0)
    for sFileName in argv:
        if not os.path.isfile(sFileName):
            print "ERROR: %s does not exist, ignoring" % sFileName
            continue
        log.info("Reading file %s" % sFileName)
        oFile = open(sFileName, 'r')
        dImportData = json.loads(oFile.read())
        oFile.close()
        # Special fields that require 'processing'
        dImportData = specialFieldProcessing(dImportData, warn=True)
        # The order which triggers, notifications, windows are applied are
        # important. So read file file and store it.
        if ".trigger." in sFileName:
            lTriggers.append(dImportData)
        elif ".notification." in sFileName:
            lNotifications.append(dImportData)
        elif ".window." in sFileName:
            lWindows.append(dImportData)
    # Apply Triggers, then Notifications, and finally windows
    for dImportData in lTriggers + lNotifications + lWindows:
        if dImportData in lTriggers:
            type = "trigger"
            log.info("Evaluating %s '%s'" % (type, dImportData['name']))
            # Name Index of Notifications set in Zenoss
            if len(dTrigsIndex) == 0:
                dTrigsIndex = getNameIdx(type)
        elif dImportData in lNotifications:
            type = "notification"
            log.info("Evaluating %s '%s'" % (type, dImportData['name']))
            # Name Index of Notifications set in Zenoss
            if len(dNotifsIndex) == 0:
                dNotifsIndex = getNameIdx(type)
        elif dImportData in lWindows:
            type = "window"
            log.info(("Evaluating notification schedule window '%s', for"
                   "notification '%s'") % (
                        dImportData['name'],
                        dImportData['uid'].split('/')[4]
                    )
            )
            # Name Index of Windows in Zenoss
            if dWinsIndex == {}:
                dWinsIndex = getNameIdx(type)
        else:
            print "ERROR: unknown type"
            exit(1)
        # Create Notification
        dZenConfig = getConfigOrCreate(type, dImportData)
        # Update Notification
        updateZenoss(type, dImportData)
        # compare, confirm update applied
        diffData(type, dImportData)
    log.info("Script completed")
