#!/usr/bin/env python
#################################################
# This script was written as a proof of concept #
# for adding devices to a system from a csv file#
#                                               #
# the name of the csv file is devices.csv       #
# the format of the csv file is:                #
#        deviceId, deviceClass, productionState #
# This could easily be extended to include      #
# values like collector, manageIp, etc          #
#################################################

import zenApiLib

clean_csv = []

csv_file = open('devices.csv', 'r').readlines()
for line in csv_file:
    clean_line = line.replace('\n', '')
    clean_line.strip()
    clean_csv.append(clean_line)

dr = zenApiLib.zenConnector(routerName='DeviceRouter')
for line in clean_csv:
    split_csv = line.split(',')
    dev_name = split_csv[0].strip()
    dev_class = split_csv[1].strip()
    prod_state = split_csv[2].strip()
    response = dr.callMethod('addDevice', deviceName=dev_name, deviceClass=dev_class, productionState=prod_state)
    print response
