from zenApiLib import ZenAPIConnector
import zenApiLib

class ZenDeviceUuidFinder():
    '''
    This class returns the name and UUID of a device when
    provided a query
    '''
    def __init__(self, query):
        self.uuid = None
        self.results = []
        self.log = logging.getLogger('zenApiDeviceRouterHelper.ZenDeviceUuidFinder')
        deviceAPI = zenApiLib.zenConnector(routerName = 'DeviceRouter')
        apiResults = deviceAPI.callMethod('getDeviceUuidsByName', query = query)
        for resp in apiResults:
            if resp['result']['sucess']:
                self.results += resp['result']['data']
            else:
                self.log.error('Non-sucessful result returned: %s' % resp)
        self.count = len(self.results)

    def getFirstUuid(self):
        try:
            return self.result[0]['uuid']
        except (KeyError, TypeError):
            return None

    def getAllUuids(self):
        try:
            return [x['uuid'] for x in self.result]
        except (KeyError, TypeError):
            return None

    def getCount(self):
        return self.count

    def first(self):
        return self.getFirstUuid()


class ZenDeviceUidFinder():
    '''
    This class returns the name and UID (path) of a device when
    provided a query
    '''
    def __init__(self, name=None, ip=None):
        self.router = 'DeviceRouter'
        self.method = 'getDevices'
        self.params = {}
        if name is not None:
            self.params['name'] = name
        if ip is not None:
            self.params['ipAddress'] = ip
        self.data = {'params': self.params}
        self.api_call = zenApiLib.zenConnector()
        self.api_call.setRouter(self.router)
        self.response_json = self.api_call.callMethod(self.method, **self.data)
        self.count = len(self.response_json['result']['devices'])

    def getFirstUid(self):
        try:
            return self.response_json['result']['devices'][0]['uid']
        except (KeyError, TypeError):
            return None

    def getAllUids(self):
        try:
            return [x['uid'] for x in self.response_json['result']['devices']]
        except (KeyError, TypeError):
            return None

    def getCount(self):
        return self.count

    def first(self):
        return self.getFirstUid()
