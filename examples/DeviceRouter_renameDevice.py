# Re id a device 
#!/bin/env python
import zenApiLib
from zenApiDeviceRouterHelper import ZenDeviceUidFinder
from zenApiJobsRouterHelper import watchStatus
import argparse
import sys
import logging
from pprint import pprint

def buildArgs():
    parser = argparse.ArgumentParser(description='Rename Device')
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-c', dest='configSection', action='store',
                        metavar="credsSection", default='default',
                        help='zenApiLib credential configuration section '
                        '(default)')
    parser.add_argument('-o', dest='outFileName', action='store', default=None,
                        help="Output to file instead of stdout.")
    parser.add_argument('-d', dest='deviceName', action='store',  default=None,
                        required=True, help="Device Name (ID).")
    parser.add_argument('-n', dest='newDeviceName', action='store', default=None,
                        required=True, help="Desired New Device Name (ID).")
    parser.add_argument('-r', dest='dontMoveGraphData', action='store_true',
                        help="Do NOT retain graph data for the device. ")
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)
    args = vars(buildArgs())
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    if args['outFileName']:
        rOut = open(args['outFileName'], 'w')
    else:
        rOut = sys.stdout
    api = zenApiLib.zenConnector(
                        cfgFilePath=args['configFilePath'],
                        section=args['configSection'],
                        loglevel=args['loglevel'])
    api.setRouter('DeviceRouter')
    if args['dontMoveGraphData']:
	retainData = False
    else:
        retainData = True
	
    # Rename specified device
    deviceName = args['deviceName']
    newDeviceName = args['newDeviceName']
    results = ZenDeviceUidFinder(name=deviceName)
    if results.getCount() != 1:
       print >> sys.stderr, 'Skipping "{}", found {} devices.'.format(deviceName, results.getCount())
       sys.exit()
        
    devUid = results.getFirstUid()
    apiResult = api.callMethod(
       'renameDevice',
            uid=devUid,
            newId=newDeviceName,
            retainGraphData=retainData
        )
    if not apiResult['result']['success']:
       print >> sys.stderr, 'Renaming API call failed'
       pprint(apiResult)
    else:
       print >> rOut, "Renaming {} to {} initiated - Keeping data {}".format(deviceName, newDeviceName, retainData)
