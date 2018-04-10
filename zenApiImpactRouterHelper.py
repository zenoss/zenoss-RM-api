import zenApiLib

IMPACT_ROOT = '/zport/dmd/DynamicServices'

class zenApiImpactRouterHelper():
    def __init__(self, debug=False):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        self.api = zenApiLib.zenConnector(section = 'default', routerName = 'ImpactRouter')

    def impact_request(self, method, data=[{}]):
        results = self.api.callMethod(method, **dict(data[0]))
        return results['result']

    def get_services_tree(self):
        return self.impact_request('getTree')[0]

    def get_service_info(self, uid):
        data = {'uid': uid}
        return self.impact_request('getInfo', [data])

    def delete_node(self, uid):
        data = {'uid': uid}
        return self.impact_request('deleteNode', [data])

    def create_organizer(self, contextUid, id):
        data = dict(contextUid=contextUid, id=id)
        return self.impact_request('addOrganizer', [data])

    def create_service(self, contextUid, id):
        data = dict(contextUid=contextUid, id=id)
        return self.impact_request('addNode', [data])

    def add_impact(self, parentUid, childUids):
        if isinstance(childUids, basestring):
            childUids = [childUids]
        data = dict(targetUid=parentUid, uids=childUids)
        return self.impact_request('addToDynamicService', [data])

    # Extending the api_helper.py for setting policy gates
    def set_policy(self, serviceUid, contextUid, policyType, dependentState, state, threshold, triggerType):
        data = {
            "permissionUid": serviceUid, 
            "contextUid": contextUid, 
            "uid": serviceUid, 
            "policyType": policyType,
            "data": {
                "dependentState":dependentState, 
                "state": state, 
                "threshold": threshold, 
                "triggerType": triggerType, 
                "metaTypes":[] 
                }
            }
        return self.impact_request('addStateTrigger', [data])

    def get_policies(self, contextUid, serviceUid, policyType):
        data = { 
            "contextUid": contextUid, 
            "uid": serviceUid, 
            "policyType": policyType,
            }
        return self.impact_request('getStateTriggers', [data])
