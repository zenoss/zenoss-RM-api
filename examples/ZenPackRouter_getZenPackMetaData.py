#!/usr/bin/env python
from __future__ import print_function

import zenApiLib

if __name__ == '__main__':
    zenApi = zenApiLib.zenConnector()
    zenApi.setRouter('ZenPackRouter')
    apiResp = zenApi.callMethod('getZenPackMetaData')
    for zpKey in sorted(apiResp['result']['data']):
        zpMeta = apiResp['result']['data'][zpKey]
        print(zpMeta['name'], zpMeta['version']) 
