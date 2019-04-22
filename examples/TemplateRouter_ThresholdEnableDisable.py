#!/bin/env python
# Enable or disable a threshold
import zenApiLib
import argparse
import sys
import logging
from pprint import pformat

def buildArgs():
    parser = argparse.ArgumentParser(description='Enable the specified threshold',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-c', dest='configSection', action='store',
                        default='default',
                        help='zenApiLib credential configuration section')
    parser.add_argument('--deviceclass', dest='devClass', action='store',
                        default="/",
                        help='DeviceClass path for bound template on e.g. /, /Server etc')
    parser.add_argument('-t', dest='templateName', action='store',
                        required=True, help='Template Name')
    parser.add_argument('-n', dest='thresholdName', action='store',
                        required=True, help='Threshold Name')
    parser.add_argument('-d', dest='disable', action='store_true',
                        help='Disable threshold rather than enable')
    return parser.parse_args()


def getDeviceClassTemplates(path='/', tmplTree=[]):
    dcTemplates = {}

    # Retrieve the entire template tree, once
    if not tmplTree:
        apiRawResult = api.callMethod('getDeviceClassTemplates', id="/zport/dmd/Devices")
        if not apiRawResult.get('success', True):
            log.error('Issue getting template tree\n{}'.format(pformat(apiRawResult)))
            sys.exit(1)
        tmplTree = apiRawResult['result']
        log.debug('Template tree:\n{}'.format(pformat(apiRawResult)))

    for tmplNode in tmplTree:
        log.debug('Checking {} against {}'.format(path,tmplNode['path']))

        if tmplNode['path'] == path:
            # Found our target deviceClass. Now look at the templates bound here
            for template in tmplNode['children']:
                if not template['isOrganizer']:
                    dcName, tmplName = template['path'].split('/rrdTemplates/')
                    # Check if we've found the specified template
                    if tmplName == args['templateName']:
                       dcTemplates[template['path']] = {
                          'deviceclassName': dcName,
                          'templateName': tmplName}
                       log.debug('Found at {} at {}'.format(args['templateName'],path))
            break
        elif tmplNode['path'] not in path:
            # Not our target device class, moving on
            log.debug('{} is not in {} continuing search'.format(tmplNode['path'],path))
            continue
        else:
            # Following the tree downwards
            dcTemplates.update(getDeviceClassTemplates(path, tmplNode['children']))
    return dcTemplates

def getTemplateThresholds(uid):
    apiRawResult = api.callMethod('getThresholds',
                                   uid=uid)
    if not apiRawResult.get('success', True):
        log.error('Issue getting template thresholds for template {}\n{}'.format(uid,pformat(apiRawResult)))
        sys.exit(1)
    return apiRawResult['result']['data']

def enableThreshold(uid, enable = True):
    apiRawResult = api.callMethod('setInfo',
                                   uid=uid,
                                   enabled=enable)
    if not apiRawResult.get('success', True):
        log.error('Issue setting threshold {} state to {}\n{}'.format(uid,enable,pformat(apiRawResult)))
        sys.exit(1)
    else:
        log.info('Successfully set threshold {} state to {}\n{}'.format(uid,enable,pformat(apiRawResult)))

    return apiRawResult['result']['data']

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    args = vars(buildArgs())
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    api = zenApiLib.zenConnector(
                    routerName='TemplateRouter',
                    cfgFilePath=args['configFilePath'],
                    section=args['configSection'],
                    loglevel=args['loglevel'])
    if api.config['timeout'] < 30:
        api.config['timeout'] = 30
    rOut = sys.stdout

    # Specified device class must start with /
    if not args['devClass'].startswith('/'):
        log.error('If specified, device class must start with a "/"')
        sys.exit(1)

    # Try to find the specified template
    targetedTemplates = getDeviceClassTemplates('Devices' + args['devClass'])

    if len(targetedTemplates) == 0:
    # Specified template couldn't be found
        log.error('Could not find template {} on device class {}'.format(args['templateName'],args['devClass']))
        sys.exit(1)

    foundThreshold = False
    # Loop through thresholds on the found template targeted deviceClass templates
    for tmplPath, tmplDict in targetedTemplates.items():
        templThresholds = getTemplateThresholds(tmplPath)
        log.debug('Thresholds\n{}'.format(pformat(templThresholds)))
        for threshold in templThresholds:
           log.debug('Threshold\n{}'.format(pformat(threshold)))
           log.debug('Checking found threshold {} against {}'.format(threshold['name'],args['thresholdName']))
           if threshold['name'] == args['thresholdName']:
               foundThreshold = True
               log.debug('Found threshold {} on template {} at {}'.format(args['thresholdName'],args['templateName'],threshold['uid']))
               break

    if not foundThreshold:
    # Specified threshold couldn't be found
        log.error('Found template {} at {} but it does not have a threshold named {}'.format(args['templateName'],args['devClass'],args['thresholdName']))
        sys.exit(1)
    else:
        log.info('Found threshold "{}" on template {} at device class {}. Current state is {}'.format(args['thresholdName'],args['templateName'],args['devClass'],threshold['enabled']))

    # Set the threshold to desired state
    if args['disable']:
       enableThreshold(threshold['uid'],enable = False)
    else:
       enableThreshold(threshold['uid'])

    sys.exit(0)
