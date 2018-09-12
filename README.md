# Overview

This repository is a fork of https://github.com/amccurdy/zenoss_api and currently the original python library _ZenAPIConnector.py_ still exists in this repo. A new python library _zenApiLib.py_ has been introduced with this forked repo.

# zenApiLib
**File**: zenApiLib.py

**Description**: New python library introduced in this git-hub repository

**Functionality**:
- leverages python logging library
- paging api support; leverage router methods 'limit' parameter to break large results queries into manageable chunks
- api result error checking
    - Content-Type JSON, return decoded json object
    - Content-Type HTML, return error w/ HTML page title
    - Misc
- api call error checking
    - Validate specified Router exists
    - Validate called method exists
- backward compatibility w/ zenoss_api.ZenAPIConnector.ZenAPIConnector
- support multiple zenoss instance definitions in credential file
    - credential file name defaults to 'creds.cfg' and same directory as zenApiLib.py file
    - ability to specify credential file
- 'zenApiCli.py' script available. For simple, command line API interaction. Can be easily incorporated with existing shell scripts.

## Pre-requisites:
This python library depends on the following: requests, pyOpenSSL, ndg-httpsclient, pyasn1

You can install those quickly with pip:
```
yum -y install python-pip
pip install requests pyOpenSSL ndg-httpsclient pyasn1
```

## Environment:

If your script(s) are not in the same directory as `zenApiLib.py` or the standard python lib directories, then update your `$PYTHONPATH` environment variable to include that directory.

_Note_: The credentials `creds.cfg` file by default is expected to be in the same directory as `zenApiLib.py`. A different location can be specified at instantiation.

## Usage:

### zenApiCli.py

   1. Script help output:
   
      ```
      $ ./zenApiCli.py --help
        usage: zenApiCli.py [-h] [-v LOGLEVEL] [-t TIMEOUT] -r routerName -m
                            routerMethodName [-c credsSection] [-p credsFilePath]
                            [-d KEY1=VAL1,KEY2=VAL2...] [-x fieldName.fieldName...]

        Command Line Interface to Zennos JSON API, can be used to make simple API
        calls.

        optional arguments:
          -h, --help            show this help message and exit
          -v LOGLEVEL           Set script logging level (DEBUG=10, INFO=20, WARN=30,
                                *ERROR=40, CRTITICAL=50
          -t TIMEOUT            Override API call creds file timeout setting
          -r routerName         API router name
          -m routerMethodName   API router method to use
          -c credsSection       zenApiLib credential configuration section (default)
          -p credsFilePath      Default location being the same directory as the
                                zenApiLib.pyfile
          -d KEY1=VAL1,KEY2=VAL2...
                                Parameters to pass to router's method function
          -x fieldName.fieldName...
                                Return value from API result field. Default:
                                'result.success'. Special keyword 'all' to dump API
                                results.
      ```
  
   1. Send an event:
      ```
      ./zenApiCli.py -r EventsRouter -m add_event -d summary="this is a test",component="test" -d device="Null" -d severity=4,evclass="/Status" -d evclasskey="sma"
      ```

   1. Get device's productionState value:
      ```
      ./zenApiCli.py -r DeviceRouter -m getDevices -d uid="/zport/dmd/Devices/ControlCenter" -d params="{'ipAddress': '10.88.111.223'}" -x result.devices.0.productionState
      ```
   1. Get all devices in a deviceClass and their statuses:
      ```
      ./zenApiCli.py -r DeviceRouter -m getDevices -d uid="/zport/dmd/Devices",keys='["name","status"]' -x result.devices.*.name -x result.devices.*.status
      ```

### zenApiLib.py

   Once the **zenApiLib** library is imported you can then instantiate _zenConnector_ a few different ways:

   1. get all triggers
      ```
      import zenApiLib
      zenApi = zenApiLib.zenConnector()
      zenApi.setRouter('TriggersRouter')
      print zenApi.callMethod('getTriggers')
      ```

   1. get all devices
      ```
      import zenApiLib
      dr = zenApiLib.zenConnector(routerName = 'DeviceRouter')
      print dr.callMethod('getDevices')
      ```

   1. copy trigger from one zenoss instance to another
      ```
      import zenApiLib
      tr5 = zenApiLib.zenConnector(section = '5x', routerName = 'TriggersRouter')
      tr6 = zenApiLib.zenConnector(section = '6x', routerName = 'TriggersRouter')
      migrate = tr5.callMethod('getTrigger', uuid = "e9ac462f-a80e-4f62-83e2-5f410818d782")
      # TODO: below is incorrect, but you get the general idea
      tr6.callMethod('addTrigger' **dict(migrate['result'])
      ```

   1. get all devices, via multiple queries. limits max number of results per query to two.
      ```
      import zenApiLib
      dr = zenApiLib.zenConnector(routerName = 'DeviceRouter')
      for apiResp in dr.pagingMethodCall('getDevices', limit = 2, keys = ["productionState", "id"]):
         print apiResp
      ```

   1. send an event & check success
      ```
      import zenApiLib
      er = zenApiLib.zenConnector(routerName = 'EventsRouter')
      evtResp = er.callMethod('add_event', 
          summary = "Device in Maintenance too long !",
          device ="localhost",
          component = "",
          severity = 2,
          evclasskey = "",
          evclass = "/Status/Zenoss"
      )
      if not evtResp['result']['success']:
          print("sendEvent - nonSucessful results\n%s" % evtResp)
      ```

## API Router Helper Libraries:
**Files**: zenApiDeviceRouterHelper.py, zenApiImpactRouterHelper.py

Helper libraries that are router specific, should contain common, repeatbly used functionality.

