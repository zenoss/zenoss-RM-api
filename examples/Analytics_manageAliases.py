#!/bin/env python
import zenApiLib
import argparse
import sys
import logging
import re

import time
from pprint import pformat

HELP = '''
This script processes the specified file (default aliases.txt in the current working directory)
containing alias definitions. It will either add or remove the aliases.

Each line in the specified file should contain an alias definition
consisting of the following 6 values, pipe delimited:

  template binding path|template|datasource|datapoint|alias|rpn

Empty lines or comments beginning with # are ok. Comments can follow an alias
definition. 

Note that output of the "dumpAliases.py" script is exactly in this format ie typical usage is
to use isome ssubset of the output of dumpAliases.py as input to this script.

For each line in the input file it will print some codes and then the line.

Codes in the first column indicate the script is adding (+),
modifying the RPN (R), or removing (-) an alias.

Codes in the second column indicate an inability to process the line (X),
to find the path (c), template (t), datasource/datapoint (d), or alias (a) OR an unwillingness to remove
an alias because its defined RPN does not match (r). The latter 2 codes,
a and r, only occur when using 'remove'.

Use the script without '--commit' to see what will be changed on your monitoring templates. Modify
input files as needed, and when the changes are satisfactory, use '--commit'
to actuall make them to your monitoring templates,
'''

def buildArgs():
    parser = argparse.ArgumentParser(description=HELP, formatter_class=argparse.RawTextHelpFormatter)
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
    parser.add_argument('-o', dest='inFileName', action='store', default=None,
                        help="Read from file")
    parser.add_argument('--action', dest='action', required=True, help='[wit'
                        'h|without] - specify whether to dump datatpoints with'
                        ' aliases or those without aliases')
    parser.add_argument('--commit', dest='commit', action='store_true', 
                        help = 'Commit aliases changes to ZODB? Default is not '
                        'to commit')
    return parser.parse_args()


def rreplace(s, old, new):
    return (s[::-1].replace(old[::-1],new[::-1], 1))[::-1]
    
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

    if args['commit']:
        print "Commit turned on, changes will be commited via the API"
    else:
        print "Dry run only - no changes will be commited. Reun with --commit after reviewing output."

    # now that we've validated args, open the aliases file and loop through it looking for specified aliases in dmd
    with open(args['inFileName']) as fp:
        for line in fp:
            lineChunk = line.split('#')[0].strip()
            if not lineChunk:
    #               print '  ', line.rstrip()
                continue

            # Parse the current line into its constituent parts
            try:
                path, tplId, dsId, dpId, aliasId, rpnFormula = lineChunk.split('|')
            except ValueError:
                # Malformed line
                print ' X',line
                continue

            # Do not need to get Template or DataSource Details...
            # Get DataPoint details from API
            dsUid = "/".join([path, 'rrdTemplates', tplId, 'datasources', dsId, 'datapoints', dpId ])
            apiDataPoint = api.callMethod('getDataPointDetails',
                                           uid=dsUid)
            if not apiDataPoint['result'].get('record', False):
                defaultMsg = 'Unsuccessful API call getting "%r" dataPoint details'.format(
                                    templ['uid'])
                log.error(apiDataPoint['result'].get('msg', defaultMsg))
                continue
            #print pformat(apiDataPoint)
            # With a valid datapoint let's iterate over all the aliases there looking for an alias match
            alias = None
            aliasCount = 0
            for als in apiDataPoint['result']['record']['aliases']:
                if als['name'] == aliasId:
                    # Found the alias
                    alias = als
                    rmAlias = apiDataPoint['result']['record']['aliases']
                    rmAlias.pop(aliasCount)
                    break
                aliasCount+=1

            # If we're attempting to add an alias...
            if args['action'] == 'add':
                if alias:
                    # We found the alias...

                    formula = alias.get('formula', '')
                    formula = '' if formula is None else formula
                    if formula == rpnFormula:
                        # We found the alias, and the RPN matches, so log a match, nothing to do
                        print '  ', line.rstrip()
                    else:
                        # We found the alias, but we need to update the RPN, so log an RPN update
                        print 'R ', line.rstrip()
                        if args['commit']:
                            apiDPChg = api.callMethod('setInfo',
                                               uid = dsUid,
                                               aliases = [{
                                                            "id": alias['name'],
                                                            "formula": rpnFormula
                                                         }]
                                               )
                            if not apiDPChg['result']['success']:
                                print >>sys.stderr, "Formula change for alias '{}' was not successful. {}".format(
                                    dsUid,
                                    pformat(apiDPChg)
                                )
                            sys.exit()
                else:
                    # We didn't find the alias, so add it and the RPN, if any, and log an add
                    print '+ ', line.rstrip()
                    if args['commit']:
                        apiDPChg = api.callMethod('setInfo',
                                           uid = dsUid,
                                           aliases = [{
                                                        "id": aliasId,
                                                        "formula": rpnFormula
                                                     }]
                                           )
                        if not apiDPChg['result']['success']:
                            print >>sys.stderr, "Formula change for alias '{}' was not successful. {}".format(
                                dsUid,
                                pformat(apiDPChg)
                            )
            # If we're attempting to remove an alias...
            elif args['action'] == 'remove':
                if alias:
                    # We found the alias...

                    formula = alias.get('formula', '')
                    formula = '' if formula is None else formula
                    if formula == rpnFormula:
                        # We found the RPN matches, so remove the alias and RPN and log a removal
                        print '- ', line.rstrip()
                        #datapoint.removeAlias(aliasId)
                        if args['commit']:
                            apiDPChg = api.callMethod('setInfo',
                                               uid = dsUid,
                                               aliases = rmAlias)
                            if not apiDPChg['result']['success']:
                                print >>sys.stderr, "Formula change for alias '{}' was not successful. {}".format(
                                    dsUid,
                                    pformat(apiDPChg)
                                )                        
                    else:
                        # We RPN doesn't match so log the inability to remove the alias and RPN due to RPN mismatch
                        print ' r', line.rstrip()
                else:
                    # We couldn't find the alias, so log the inability to find the alias
                    print ' a', line.rstrip()
