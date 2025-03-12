#!/usr/bin/env python
# ####################################
# Copyright (C) Zenoss, Inc. 2025, all rights reserved.
# list installed ZenPacks and versions
######################################

from __future__ import print_function
import time
import zenApiLib

if __name__ == '__main__':

    #Currently drops a dated file to the current directory, feel free to add a path ie:
    #f = open('/desired/path/here/zenpack_list-'+time.strftime("%Y-%m-%d-%H%M%S")+'.csv','w')
  
    f = open('zenpack_list-'+time.strftime("%Y-%m-%d-%H%M%S")+'.csv','w')
    print('Name Version')
    l="Name Version\n"
    f.write(l)
    zenApi = zenApiLib.zenConnector()
    zenApi.setRouter('ZenPackRouter')
    apiResp = zenApi.callMethod('getZenPackMetaData')
    for zpKey in sorted(apiResp['result']['data']):
        zpMeta = apiResp['result']['data'][zpKey]
        l=zpMeta['name'] + zpMeta['version'] +"\n"
        print(zpMeta['name'], zpMeta['version'])
        f.write(l)
    f.close()
