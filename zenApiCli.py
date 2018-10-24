#!/usr/bin/env python
from zenApiLib import zenConnector
import argparse
import json
import logging
from pprint import pprint
import sys


class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        my_dict = getattr(namespace, self.dest, {})
        if my_dict is None:
            my_dict = {}
        # Special routine, dealing when commas are in the value strings
        # -Strategey; find 1st equal sign, and then the 2nd equal sign.
        # -    From the 2nd equal sign string position, reverse search for
        # -    comma. That comma delimits the split between passed parameters
        # -    and ignores commas that are part of the passed parameters
        # -    value.
        sSplit = []
        sRaw = values
        while sRaw:
            firstEqualS = sRaw.find("=")
            seconEqualS = sRaw.find("=", firstEqualS + 1)
            if seconEqualS == -1:
                sSplit.append(sRaw)
                sRaw = ''
                continue
            commaPos = sRaw[0:seconEqualS].rfind(",")
            if commaPos == -1:
                log.error('TODO ERROR')
                break
            sSplit.append(sRaw[0:commaPos])
            sRaw = sRaw[commaPos+1:]
        for kv in sSplit:
            k, v = kv.split("=")
            if "{" in v or "[" in v:
                v = v.replace("'", '"')
                my_dict[k] = json.loads(v)
            else:
                if v.isdigit():
                    my_dict[k] = int(v)
                else:
                    my_dict[k] = v
        setattr(namespace, self.dest, my_dict)


def buildArgs():
    parser = argparse.ArgumentParser(
        description='Command Line Interface to Zennos JSON API, can be used '
        'to make simple API calls.')
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-t', dest='timeout', action='store', type=int,
                        help='Override API call creds file timeout setting') 
    parser.add_argument('-r', dest='rName', action='store',
                        metavar="routerName", required=True, help='API '
                        'router name')
    parser.add_argument('-m', dest='rMethod', action='store',
                        metavar="routerMethodName", required=True, help='API '
                        'router method to use')
    parser.add_argument('-c', dest='configSection', action='store',
                        metavar="credsSection", default='default',
                        help='zenApiLib credential configuration section '
                        '(default)')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-d', dest='data', action=StoreDictKeyPair,
                        default={}, metavar="KEY1=VAL1,KEY2=VAL2...",
                        help="Parameters to pass to router's method function")
    parser.add_argument('-x', dest='rFields', action='append',
                        metavar="fieldName.fieldName...", default=[],
                        help="Return value from API result field. Default: "
                        "'result.success'.\n Special keyword 'all' to dump API "
                        "results.")
    return parser.parse_args()


def nested_get(input_dict, nested_key):
    '''
    Pull a value from a nested dictionaries/lists
    TODO: Able to work with wildcards, 'result.events.*.evid' or
    'result.events.*.DeviceGroups.*.name', but needs work...
    need a use case to flesh out
    '''
    internal_dict_value = input_dict
    for k in nested_key:
        if k.isdigit():
            try:
                internal_dict_value = internal_dict_value[int(k)]
            except IndexError:
                internal_dict_value = None
        elif k == '*':
            wcPos = nested_key.index('*')
            wcValue = []
            for wcEntry in internal_dict_value:
                wcTmp = nested_get(wcEntry, nested_key[wcPos + 1:])
                wcValue.append(wcTmp)
            internal_dict_value = wcValue
            break
        else:
            internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    if isinstance(internal_dict_value, list):
        internal_dict_value = ",".join(str(k) for k in internal_dict_value)
    return str(internal_dict_value)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)
    args = vars(buildArgs())
    log = logging.getLogger('zenApiLib')
    log.setLevel(args['loglevel'])
    if args['rFields']:
        rFields = args['rFields']
    else:
        rFields = ['result.success']
    rTotalResults = {}
    # Treat all API calls like paged calls
    zenapi = zenConnector(
                routerName=args['rName'],
                cfgFilePath=args['configFilePath'],
                section=args['configSection'],
                loglevel=args['loglevel']
    )
    #cred file configuration override
    if args['timeout']:
        zenapi.config['timeout'] = args['timeout']
    for pagedResult in zenapi.pagingMethodCall(
                                        args['rMethod'],
                                        **args['data']
                                               ):
        if not nested_get(pagedResult, ['result', 'success']) != "False":
            pprint(pagedResult)
            print " "
            log.error("API success FALSE")
            sys.exit(1)
        for rFieldName in rFields:
            if rFieldName.lower() == 'all':
                pprint(pagedResult)
            else:
                if rFieldName not in rTotalResults:
                    rTotalResults[rFieldName] = nested_get(
                                                    pagedResult,
                                                    rFieldName.split('.')
                                                        )
                else:
                    rTotalResults[rFieldName] = "{},{}".format(
                                                    rTotalResults[rFieldName],
                                                    nested_get(
                                                        pagedResult,
                                                        rFieldName.split('.'))
                                                               )
    for k in rFields:
        if k == 'all':
            continue
        print "{}:{}".format(k, rTotalResults[k])
