#!/bin/env python
import zenApiLib
import argparse
import sys
import logging
import re


def buildArgs():
    parser = argparse.ArgumentParser(description='Poll & display API Router & '
                        'Method information. Wildcards can be used to "search"'
                        ' for methodNames across routers.')
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
    parser.add_argument('--aliases', dest='aliases', required=True, help='[wit'
                        'h|without] - specify whether to dump datatpoints with'
                        ' aliases or those without aliases')
    return parser.parse_args()


def getAllTemplates(templUid='/zport/dmd/Devices'):
    apiResp = api.callMethod('getTemplates', id=templUid)
    if 'result' not in apiResp:
        log.error('No template results from api query "%r"', templUid)
        return
    allTemplates = []
    if templUid != '/zport/dmd/Devices':
        return apiResp['result']
    else:
        for templ in apiResp['result']:
            if 'leaf' not in templ:
                allTemplates += getAllTemplates(templ['uid'])
        return allTemplates


def __printAliasLine(outputFile, path, dsName, dpName, alias, oid):
    if '/rrdTemplates/' in path:
        tokens = path.split('/rrdTemplates/') # device class, template
    else:
        tokens = path.rsplit('/', 1) # device specific template path, template
    tokens.append(dsName)
    tokens.append(dpName)
    # If we're printing dps with aliases, loop over the aliases printing them out
    if alias:
        tokens.append(alias['name'])
        formula = alias.get('formula', '')
        tokens.append('' if formula is None else formula)
    else:
        tokens.append(dpName)
        tokens.append('')

    if oid:
        writeStr = '%s # oid: %s' % ('|'.join(tokens), oid)
    else:
        writeStr = '%s' % ('|'.join(tokens))
    print >>outputFile, writeStr


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    args = vars(buildArgs())
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    if args['outFileName']:
        ALIAS_FILE = open(args['outFileName'], 'w')
    else:
        ALIAS_FILE = sys.stdout
    api = zenApiLib.zenConnector(
                    routerName='TemplateRouter',
                    cfgFilePath=args['configFilePath'],
                    section=args['configSection'],
                    loglevel=args['loglevel'])
    api.config['timeout'] = 30
    apiTemplates = api.callMethod('getTemplates',
                                  id='/zport/dmd/Devices')
    seenTpls = []
    ALIASES = args['aliases']
    print 'Writing all datapoints %s aliases to %s' % (ALIASES,
                                                       args['outFileName'])
    print >>ALIAS_FILE, '#template binding path|template|datasource|datapoint|alias|rpn'
    for templ in getAllTemplates():
        path = templ['uid']
        # Skip template if we're already done it
        if path in seenTpls:
            continue
        # Add template to those we're done
        seenTpls.append(path)
        # Loop for each datapoint
        apiDataPoints = api.callMethod('getDataPoints',
                                       uid=templ['uid'])
        if not apiDataPoints['result']['success']:
            log.error('Unsucessful API call getting "%r" dataPoints',
                      templ['uid'])
            continue
        for dp in apiDataPoints['result']['data']:
            # Grab the OID if it's an SNMP dp
            oid = dp.get('oid', '')  # NOTE: API does not return 'oid' field
            # Parse and format output 'token'
            dsRe = re.match(r"^.*/datasources/(.*)/datapoints.*", dp['uid'])
            dsName = dsRe.group(1)
            dpName = dp['uid'].split('/')[-1]

            # If we're printing dps with aliases, loop over the aliases printing them out
            if ALIASES == 'with':
                for alias in dp['aliases']:
                    __printAliasLine(ALIAS_FILE, path, dsName, dpName, alias, oid)

            # If we're printing dps without aliases, check there are none and print using the dp id as the default alias and no RPN
            elif not dp['aliases']:
                __printAliasLine(ALIAS_FILE, path, dsName, dpName, None, oid)
                    
    print 'Finished. All datapoints %s aliases exported to %s' % (ALIASES,
                                                                  args['outFileName'])
