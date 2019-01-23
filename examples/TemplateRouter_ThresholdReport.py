#!/bin/env python
import zenApiLib
import argparse
import sys
import logging
from pprint import pformat
import csv

initialHeader = [
        'DeviceClass',
        'Template',
        'DataSource',
        'ThresholdName',
        'ThresholdDataPoint',
        'ThresholdType']


def buildArgs():
    parser = argparse.ArgumentParser(description='Reports all defined threshol'
                        'ds in provided DeviceClass.',
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
    parser.add_argument('-o', dest='outFileName', action='store', default=None,
                        help="Write output to file")
    parser.add_argument('--deviceclass', dest='devClass', action='store',
                        default='/Devices', help='DeviceClass to report on.')
    parser.add_argument('-a', dest='includeThreshFields', action='append',
                        default=['enabled', 'severity', 'escalateCount', 'minval', 'maxval', 'description', 'explanation', 'resolution'],
                        help='Include threshold field in report.')
    parser.add_argument('--showInheritedTemplates', dest='showInherited',
                        action='store_true', help='Show Templates that are inherited.')
    parser.add_argument('--showUnboundTemplates', dest='showUnbound',
                        action='store_true', help='Show Templates that are not bound.')
    parser.add_argument('--showAllDataSources', dest='showAllDS', action='store_true',
                        help='Show all DataSources, even if there is no threshold.')
    return parser.parse_args()


def getDeviceClassTemplates(id='Devices', tmplTree=[]):
    dcTemplates = {}
    boundTmplIconCls = ('tree-template-icon-bound', 'tree-template-icon-component')
    if id[0] == "/":
        id = id[1:]
    if not tmplTree:
        apiRawResult = api.callMethod('getDeviceClassTemplates',
                                       id="/zport/dmd/Devices")
        if not apiRawResult.get('sucess', True):
            log.error('Issue getting template deviceClass tree\n{}'.format(pformat(apiRawResult)))
            sys.exit(1)
        tmplTree = apiRawResult['result']

    for tmplNode in tmplTree:
        if tmplNode['path'] == id:
            # Found our target deviceClass. Now look at the templates bound here
            for template in tmplNode['children']:
                if not template['isOrganizer']:
                    if args['showInherited'] or id in template['path']:
                        if args['showUnbound'] or template['iconCls'] in boundTmplIconCls:
                            dcName, tmplName = template['path'].split('/rrdTemplates/')
                            dcTemplates[template['path']] = {
                                                'deviceclassName': dcName,
                                                'templateName': tmplName}
            break
        elif tmplNode['path'] not in id:
            # Not our target, moving on
            continue
        else:
            # Following the tree to the target deviceClass
            dcTemplates.update(getDeviceClassTemplates(id, tmplNode['children']))
    return dcTemplates


def getTemplateThresholds(uid):
    apiRawResult = api.callMethod('getThresholds',
                                   uid=uid)
    if not apiRawResult.get('sucess', True):
        log.error('Issue getting template deviceClass tree\n{}'.format(pformat(apiRawResult)))
        sys.exit(1)
    return apiRawResult['result']['data']


def getTemplateDataSources(uid):
    apiRawResult = api.callMethod('getDataSources',
                                   uid=uid)
    if not apiRawResult.get('sucess', True):
        log.error('Issue getting template deviceClass tree\n{}'.format(pformat(apiRawResult)))
        sys.exit(1)
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
    if args['outFileName']:
        rOut = open(args['outFileName'], 'w')
    else:
        rOut = sys.stdout

    report = csv.writer(rOut, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    report.writerow(initialHeader + map(lambda d: "thresh_{}".format(d), args['includeThreshFields']))
    targetedTemplates = getDeviceClassTemplates(args['devClass'])
    # Loop through targeted deviceClass templates
    for tmplPath, tmplDict in sorted(targetedTemplates.items(), key=lambda d: (d[1]['deviceclassName'], d[1]['templateName'].lower())):
        templThresholds = getTemplateThresholds(tmplPath)
        # Define datasource index, so DS is only listed one with '--showAllDataSources' flag
        templThreshIndex = []
        if args['showAllDS']:
            tmpDS = []
            for threshold in templThresholds:
                for ds_dp in threshold['dsnames']:
                    dsName = ds_dp.split('_')[0]
                    templThreshIndex.append(dsName)
            for datasource in getTemplateDataSources(tmplPath):
                if datasource['name'] not in templThreshIndex:
                    tmpDS.append({
                            'dsnames': ["{}_{}".format(datasource['name'], "")],
                            'name': "",
                            'type': ""})
            templThresholds += tmpDS
        # Loop through all template thresholds (or all datasources + thresholds)
        for threshold in sorted(templThresholds, key=lambda d: d['name']):
            for ds_dp in threshold['dsnames']:
                dsName = ds_dp.split('_')[0]
                output = [
                        tmplDict['deviceclassName'],
                        tmplDict['templateName'],
                        dsName,
                        threshold['name'],
                        ds_dp if ds_dp[-1] != "_" else "",
                        threshold['type']]
                for threshField in args['includeThreshFields']:
                    output.append(threshold.get(threshField, ""))
                report.writerow(output)
