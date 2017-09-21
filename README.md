# Zenoss API Connector
This repo contains code that can be used to leverage the Zenoss JSON API. 

To prepare your environment, you'll need python installed, as well as the following libraries: requests, pyOpenSSL, ndg-httpsclient, pyasn1

You can install those quickly with pip:
```
yum -y install python-pip
pip install requests pyOpenSSL ndg-httpsclient pyasn1
```

To get started, edit the `creds.cfg` file to point to your Zenoss instance. You'll also need to specify a username and password, as well as specify whether or not you want to enable certificate validation. 

To make any API calls with the ZenAPIConnector, you'll need the following files from this repository: 

 - `creds.cfg`
 - `ZenAPIConnector.py`
 - `RouterEndpointMap.py`

From there, you can import the ZenAPIConnector and instantiate it. It takes 3 arguments: 

- `router` - the name of the router you want to use
- `method` - the name of the method you want to execute
- `data` - a dictionary containing any information that needs to be passed to the method

The `send()` method makes the HTTP request to the API and returns a response object. The response has a `json()` method that contains the JSON response in python format. 

# Example 

```
from ZenAPIConnector import ZenAPIConnector
router = 'DeviceRouter'
method = 'getDevices'
data = {'limit': 200}
api = ZenAPIConnector(router, method, data)
response = api.send()
print response

```


