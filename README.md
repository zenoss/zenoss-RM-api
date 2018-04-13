verview

This repository is a fork of https://github.com/amccurdy/zenoss_api and currently the original python library _ZenAPIConnector.py_ still exists in this repo. A new python library _zenApiLib.py_ has been introduced with this forked repo.

# zenApiLib (_new_)
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

Once the **zenApiLib** library is imported you can then instantiate _zenConnector_ a few different ways:

_example 1_: get all triggers
```
import zenApiLib
zenApi = zenApiLib.zenConnector()
zenApi.setRouter('TriggersRouter')
print zenApi.callMethod('getTriggers')
```

_example 2_: get all devices
```
import zenApiLib
dr = zenApiLib.zenConnector(routerName = 'DeviceRouter')
print dr.callMethod('getDevices')
```

_example 3_: copy trigger from one zenoss instance to another
```
import zenApiLib
tr5 = zenApiLib.zenConnector(section = '5x', routerName = 'TriggersRouter')
tr6 = zenApiLib.zenConnector(section = '6x', routerName = 'TriggersRouter')
migrate = tr5.callMethod('getTrigger', uuid = "e9ac462f-a80e-4f62-83e2-5f410818d782")
# TODO: below is incorrect, but you get the general idea
tr6.callMethod('addTrigger' **dict(migrate['result'])
```

_example 4_: get all devices, via multiple queries. limits max number of results per query to two.
```
import zenApiLib
dr = zenApiLib.zenConnector(routerName = 'DeviceRouter')
for apiResp in dr.pagingMethodCall('getDevices', limit = 2, keys = ["productionState", "id"]):
   print apiResp
```

_example 5_: send an event & check success
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

------

# Zenoss API Connector (_previous_)
**File**: ZenAPIConnector.py, RouterEndpointMap.py

**Description**: The orignial python library, part of the zenoss_api repository

This repo contains code that can be used to leverage the Zenoss JSON API. 

To prepare your environment, you'll need python installed, as well as the following libraries: requests, pyOpenSSL, ndg-httpsclient, pyasn1

You can install those quickly with pip:
```
yum -y install python-pip
pip install requests pyOpenSSL ndg-httpsclient pyasn1
```

If your scripts that leverage the ZenAPIConnector are in a different directory than `ZenAPIConnector.py`, `RouterEndpointMap.py`, and `creds.cfg`, then you'll need to:
 - Update `ZenAPIConnector.py` to include the absolute path to its config file
 - Make sure your `$PYTHONPATH` environment variable contains the path to the directory containing `ZenAPIConnector.py` and `RouterEndpointMap.py`

To get started, edit the `creds.cfg` file to point to your Zenoss instance. You'll also need to specify a username and password, as well as specify whether or not you want to enable certificate validation. 

To make any API calls with the ZenAPIConnector, you'll need the following files from this repository: 

 - `creds.cfg`
 - `ZenAPIConnector.py`
 - `RouterEndpointMap.py`

Update `ZenAPIConnector.py` to include the absolute path to your `creds.cfg` file. On my test box, I'm simply using a directory inside the root user's home directory.

From there, you can import the ZenAPIConnector and instantiate it. It takes 3 arguments: 

- `router` - the name of the router you want to use
- `method` - the name of the method you want to execute
- `data` - a dictionary containing any information that needs to be passed to the method

The `send()` method makes the HTTP request to the API and returns a response object. The response has a `json()` method that returns the JSON response in python format. 

## Example 

```
from ZenAPIConnector import ZenAPIConnector
router = 'DeviceRouter'
method = 'getDevices'
data = {'limit': 200}
api = ZenAPIConnector(router, method, data)
response = api.send()
print response.json()

```

