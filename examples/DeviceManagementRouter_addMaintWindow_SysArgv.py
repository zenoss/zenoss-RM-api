#!/usr/bin/env python
from __future__ import print_function
import zenApiLib
import time
import sys

usage = '%s <uid> <durationHours> <prodState> <name>' % (sys.argv[0])

if len(sys.argv) != 5:
    print(usage)
    sys.exit(1)
else:
    uid = sys.argv[1]
    durationHours = sys.argv[2]
    prodState = sys.argv[3]
    name = sys.argv[4]

now = int(time.time())

dmr = zenApiLib.zenConnector()

dmr.setRouter(routerName='DeviceManagementRouter')

params = {"uid": uid,
          "id": "",
          "name": name,
          "startDateTime": now,
          "durationDays":"00",
          "durationHours": durationHours,
          "durationMinutes":"00",
          "repeat":"Never",
          "startProductionState": prodState,
          "enabled": True
          }

dmr.callMethod('addMaintWindow', params=params)
