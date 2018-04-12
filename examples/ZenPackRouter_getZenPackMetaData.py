#!/usr/bin/env python

import zenApiLib

if __name__ == '__main__':
    zenApi = zenApiLib.zenConnector()
    zenApi.setRouter('ZenPackRouter')
    apiResp = zenApi.callMethod('getZenPackMetaData')
    for zpKey in sorted(apiResp['result']['data']):
        zpMeta = apiResp['result']['data'][zpKey]
        print zpMeta['name'], zpMeta['version'] 
