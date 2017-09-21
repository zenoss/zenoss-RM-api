#!/usr/bin/env python

import sys
import json
import requests

headers = {'Content-Type': 'application/json'}
base_url = 'https://zenossprodse1.saas.zenoss.com/zport/dmd/'
router = 'IntrospectionRouter'
router_endoint = 'introspection_router'
url = '%s%s' % (base_url, router_endoint)
username='api_user'
password='3FjV4LAZf78q'

payload = {'action': router, 'method': 'getAllRouters', 'tid': 1}

response = requests.post(url, data=json.dumps(payload), headers=headers, auth=(username, password))

response_json = response.json()

response_json

router_list = []
for item in response_json['result']['data']:
    router_list.append(item['action'])

router_list.sort()

for r in router_list: print r
