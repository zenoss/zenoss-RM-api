#!/usr/bin/env python
"""
zenApiImpactRouterHelper - Convenience helpers for the Zenoss ImpactRouter API.
Compatible with Python 2.7 and Python 3.6+
"""
from __future__ import print_function, absolute_import

import six
import zenApiLib

IMPACT_ROOT = '/zport/dmd/DynamicServices'


class zenApiImpactRouterHelper(object):
    def __init__(self, debug=False):
        self.api = zenApiLib.zenConnector(section='default', routerName='ImpactRouter')

    def impact_request(self, method, data=None):
        if data is None:
            data = [{}]
        results = self.api.callMethod(method, **dict(data[0]))
        return results['result']

    def get_services_tree(self):
        return self.impact_request('getTree')[0]

    def get_service_info(self, uid):
        return self.impact_request('getInfo', [{'uid': uid}])

    def delete_node(self, uid):
        return self.impact_request('deleteNode', [{'uid': uid}])

    def create_organizer(self, contextUid, id):
        return self.impact_request('addOrganizer', [dict(contextUid=contextUid, id=id)])

    def create_service(self, contextUid, id):
        return self.impact_request('addNode', [dict(contextUid=contextUid, id=id)])

    def add_impact(self, parentUid, childUids):
        if isinstance(childUids, six.string_types):
            childUids = [childUids]
        return self.impact_request('addToDynamicService', [dict(targetUid=parentUid, uids=childUids)])

    def set_policy(self, serviceUid, contextUid, policyType, dependentState, state, threshold, triggerType):
        data = {
            'permissionUid': serviceUid,
            'contextUid': contextUid,
            'uid': serviceUid,
            'policyType': policyType,
            'data': {
                'dependentState': dependentState,
                'state': state,
                'threshold': threshold,
                'triggerType': triggerType,
                'metaTypes': [],
            },
        }
        return self.impact_request('addStateTrigger', [data])

    def get_policies(self, contextUid, serviceUid, policyType):
        data = {
            'contextUid': contextUid,
            'uid': serviceUid,
            'policyType': policyType,
        }
        return self.impact_request('getStateTriggers', [data])
