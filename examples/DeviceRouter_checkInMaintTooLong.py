#!/bin/python
import argparse
import os
import json
import logging
import time
import sys
from pprint import pprint
import zenApiLib


def buildArgs():
    parser = argparse.ArgumentParser(description='Generate an event if devices have been had a ProductionState of Maintenance for too long.')
    parser.add_argument('-v', dest='loglevel', action='store',
                    type = int, default = 30,
                    help = 'Set script logging level (DEBUG=10, INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-t', dest='seconds', action='store',
                    type = int, default = 86400,
                    help = 'Maintenance theshold (default 86400 [1 day])')
    parser.add_argument('-s', dest='severity', action='store',
                    default = 4,
                    help = 'Event severity (debug=1, info=2, *warning=3, error=4, critical=5')
    parser.add_argument('-c', dest='config', action='store',
                    default = 'default',
                    help = 'zenApiLib configuration section (default)')
    return parser.parse_args()


def log2stdout(loglevel):
    '''
    Setup logging
    '''
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(loglevel)
    return logging.getLogger('checkIfMaintTooLong')


def eventTemplate():
    return { "summary": "Device in Maintenance too long !",
        "device": "Unknown",
        "component":"",
        "evclasskey": "",
        "evclass": "/Status/Zenoss"}


def getHistory(filePath = ""):
    if filePath == "":
        filePath = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__), 'checkIfMaintTooLong-History.json')
        )
    if os.path.exists(filePath):
        with open(filePath, 'r') as fp:
            history = json.load(fp)
    else:
        history = {}
    return history


def updateHistoryFile(data, filePath = ""):
    if filePath == "":
        filePath = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__), 'checkIfMaintTooLong-History.json')
        )
    with open(filePath, 'w') as fp:
        json.dump(data, fp)


def sendEvent(**evtFields):
    evtResp = evtRouter.callMethod('add_event', **evtFields)
    if not evtResp['result']['success']:
        log.warn("sendEvent - nonSucessful results\n%s" % evtResp)


if __name__ == '__main__':
    args = buildArgs()
    log = log2stdout(args.loglevel)
    devMaintHistory = getHistory()
    thisRunDevicesInMaint = []
    devRouter = zenApiLib.zenConnector(section = args.config, routerName = 'DeviceRouter')
    evtRouter = zenApiLib.zenConnector(section = args.config, routerName = 'EventsRouter')

    # Stage1: loop through all devices in ZenossRM w/ ProdState Maintenance(300)
    devInMaint = devRouter.pagingMethodCall('getDevices',
        keys = ["productionState", "id"],
        params = {"productionState": [300]},
        limit = 50
    )
    for apiResp in devInMaint:
        if not apiResp['result']['success']:
            log.warn("Steag1 - nonSucessful results 'getDevices':\n%s" % apiResp)
            sys.exit(1)
        else:
            for dev in apiResp['result']['devices']:
                log.debug("stage1 - device: %s" % dev['id'])
                thisRunDevicesInMaint.append(dev['id'])
                if not (dev['id'] in devMaintHistory):
                    log.debug("stage1 device: %s new" % dev['id'])
                    devMaintHistory[dev['id']]=time.time()
                else:
                    howLongSecs=time.time() - devMaintHistory[dev['id']]
                    if howLongSecs > args.seconds:
                        log.debug("stage1 device: %s too long !!!!" % dev['id'])
                        evtFields = eventTemplate()
                        evtFields.update({
                            "device": dev['id'],
                            "severity": args.severity,
                            "message": "Detected to be in maintenance at %s, and has been in maintenance for %d days, %d hours, and %d minutes." % (
                                time.strftime("%H:%M:%S, %Y/%m/%d %Z", time.localtime(devMaintHistory[dev['id']])),
                                (howLongSecs // 86400),
                                (howLongSecs // 3600 % 24),
                                (howLongSecs // 60 % 60)
                            )
                        })
                        sendEvent(**evtFields)
    updateHistoryFile(devMaintHistory)

    # Stage2: loop through history; send clears if device is out of maint and/or remove entry from history
    for dev in list(devMaintHistory.keys()):
        if not dev in thisRunDevicesInMaint:
            if (time.time() - devMaintHistory[dev]) > args.seconds:
                evtFields = eventTemplate()
                evtFields.update({
                    "device": dev,
                    "severity": 0,
                })
                sendEvent(**evtFields)
            del devMaintHistory[dev]
    updateHistoryFile(devMaintHistory)

    #Stage3: send a heartbeat event
    sendEvent(
        summary = "Device state check, in maintenance too long - script run",
        device = "localhost",
        component = "",
        evclasskey = "",
        evclass = "/Heartbeat",
        severity = 4,
        timeout = 600
    )