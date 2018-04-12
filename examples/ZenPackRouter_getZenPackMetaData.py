#!/usr/bin/env python

import zenApiLib

if __name__ == '__main__':
    zenApi = zenApiLib.zenConnector()
    zenApi.setRouter('ZenPackRouter')
    zps = zenApi.callMethod('getZenPackMetaData')
    for zp in zps['result']['data'].keys():
	print "%s: %s" % (zp, zps['result']['data'][zp]['version'])
