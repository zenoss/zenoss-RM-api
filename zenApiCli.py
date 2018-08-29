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
         if my_dict == None:
            my_dict = {}
         #Special routine, dealing when commas are in the value strings
         sSplit=[]
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
             k,v = kv.split("=")
             if "{" in v or "[" in v:
                v = v.replace("'", '"')
                my_dict[k] = json.loads(v)
             else:
                my_dict[k] = v
         setattr(namespace, self.dest, my_dict)


def buildArgs():
    parser = argparse.ArgumentParser(description='Primarily a python library to be used with your python scripts. When called directly, can be used to make simple API calls.')
    parser.add_argument('-v', dest='loglevel', action='store',
                    type = int, default = 30,
                    help = 'Set script logging level (DEBUG=10, INFO=20, WARN=30, *ERROR=40, CRTITICAL=50')
    parser.add_argument('-r', dest='rName', action='store', metavar="routerName",
                    required=True,
                    help = 'API router name')
    parser.add_argument('-m', dest='rMethod', action='store', metavar="routerMethodName",
                    required=True,
                    help = 'API router method to use')
    parser.add_argument('-c', dest='configSection', action='store', metavar="credsSection",
                    default = 'default',
                    help = 'zenApiLib credential configuration section (default)')
    parser.add_argument('-p', dest='configFilePath', action='store', metavar="credsFilePath",
                    default = '',
                    help = 'Default location being the same directory as the zenApiLib.py file')
    parser.add_argument('-d', dest='data', action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...",
                    help = "Parameters to pass to router's method function")
    parser.add_argument('-x', dest='rValue', action='store', metavar="fieldName.fieldName...",
                    default = 'result.success', help = "Return value from API result field. Default: 'result.success'")
    return parser.parse_args()


def nested_get(input_dict, nested_key):
    internal_dict_value = input_dict
    for k in nested_key:
        if k.isdigit():
            internal_dict_value = internal_dict_value[int(k)]
        else:
            internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value    


if __name__ == '__main__':
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)
    args = vars(buildArgs())
    log = logging.getLogger('zenApiLib')
    log.setLevel(args['loglevel'])
    zenapi  = zenConnector(routerName=args['rName'], cfgFilePath=args['configFilePath'],section = args['configSection'], loglevel = args['loglevel'])
    apiResult = zenapi.callMethod(args['rMethod'], **args['data'])
    if not nested_get(apiResult, ['result', 'success']):
        pprint(apiResult)
        sys.exit(1)
    else:
        if args['rValue'].lower() == 'all':
            pprint(apiResult)
        else:
            rValue = nested_get(apiResult, args['rValue'].split('.'))
            if rValue:
                print rValue
            else:
                print "-1"
                #print "'%s' does not exist in API results:" 
                #pprint(apiResult)
