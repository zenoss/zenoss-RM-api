#!/usr/bin/env python
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.util.retry import Retry
from httplib import HTTPConnection
from requests.adapters import HTTPAdapter
import json
import ConfigParser
from HTMLParser import HTMLParser
import logging
import copy


class ZenAPIConnector():
    '''
    Enhanced API library embedding increased functionality & error handling
    '''
    def __init__(self, section = 'default', cfgFilePath = "", routerName = None):
        self._url = ''
        self._routerName = ''
        self._tid = 0
        self.config = self._getConfigDetails(section, cfgFilePath)
        self.routerEndpointMap = self.getRouterEndpointMappings()
        self.requestSession = self.getRequestSession()
        self.log = logging.getLogger('zenApiLib.ZenAPIConnector')
        if routerName:
            self.setRouter(routerName)
        

    def _getConfigDetails(self, section, cfgFilePath):
        '''
        Read 'creds.cfg' configuration file. Default location being in the
        same directory as the python library file & return parameters in
        specific 'section'.
        '''
        configurations = ConfigParser.ConfigParser()
        if cfgFilePath == "":
            cfgFilePath = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__), 'creds.cfg')
            )
        configurations.read(cfgFilePath)
        if not (section in configurations.sections()):
            raise Exception('Specified configuration section, "%s" not defined in "%s".' % (section, cfgFilePath)) 
        configuration = {item[0]: item[1] for item in configurations.items(section)}
        configuration = self._sanitizeConfig(configuration)
        return configuration


    def _sanitizeConfig(self, configuration):
        '''
        Ensure 'creds.cfg' configuration file has required fields.
        Deal with special fields.
        '''
        if not ('url' in configuration):
            raise Exception('Configuration file missing "url" key')
        if not ('username' in configuration):
            raise Exception('Configuration file missing "username" key')
        if not ('password' in configuration):
            self.log.error('Configuration file missing "password" key')
        sslVerify = True
        if 'ssl_verify' in configuration:
            if configuration['ssl_verify'].lower() == 'false':
                sslVerify = False
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        configuration['ssl_verify'] = sslVerify
        return configuration


    def getRequestSession(self):
        '''
        Setup defaults for using the requests library 
        '''
        s = requests.Session()
        retries = Retry(total=3,
                backoff_factor=1,
                status_forcelist=[ 500, 502, 503, 504 ])
        s.mount(
            'https://',
            HTTPAdapter(max_retries=retries)
        )
        s.mount(
            'http://',
            HTTPAdapter(max_retries=retries)
        )
        return s

    def callMethod(self, *method, **payload):
        '''
        Returns an iterative, generator type object of API call results.
        Queries that return a large # of results (>50, default) will be broken
        up entries. Note not all API router method calls support splitting up
        large results into manageable chunks (e.g. getDevices vs. getTriggers)
        '''
        apiResultsReturned = 0
        apiResultsTotal = 1
        limitApiCallResults = 50
        if 'data' in payload:
            if 'start' in payload['data']:
                apiResultsReturned = payload['data'][0]['start']
            if 'limit' in payload['data']:
                limitApiCallResults = payload['data'][0]['limit']
        #
        if logging.getLogger().getEffectiveLevel() == 10:
            HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.getLogger().getEffectiveLevel())
        requests_log.propagate = True

        while (apiResultsReturned < apiResultsTotal):
            self._tid += 1
            apiBody = {
                'action': self._routerName,
                'method': method[0],
                'tid': self._tid,
                'data': [{
                    'start': apiResultsReturned,
                    'limit': limitApiCallResults
                }]
            }
            apiBody['data'][0].update(payload)
            try:
                r = self.requestSession.post(self._url,
                    auth=(self.config['username'], self.config['password']),
                    verify=self.config['ssl_verify'],
                    headers={'content-type':'application/json'},
                    data=json.dumps(apiBody),
                )
            except Exception as e:
                self.log.error('Reqests exception: %s' % e)
                yield json.dumps({'result': {'success': False} })
                apiResultsTotal = -1
            if r.status_code != 200:
                self.log.error("API call returned a '%s' http status." % r.status_code)
                self.log.debug("API EndPoint response: %s\n%s ", r.reason, r.text)
                rJson = json.dumps({'result': {'success': False} })
                apiResultsTotal = -1
            else:
                if 'Content-Type' in r.headers:
                    if 'application/json' in r.headers['Content-Type']:
                        rJson = r.json()
                        if not ('totalCount' in rJson['result']):
                            apiResultsTotal = -1
                        else:
                            apiResultsTotal = rJson['result']['totalCount']
                            apiResultsReturned = apiBody['data'][0]['start'] + len(rJson['result']['devices'])
                    elif 'text/html' in r.headers['Content-Type']:
                        parser = TitleParser()
                        parser.feed(r.text)
                        self.log.error("HTML response from API call. HTML page title: '%s'" % parser.title)
                        self.log.debug("API EndPoint response: %s\n%s ", r.reason, r.text)
                        rJson = json.dumps({'result': {'success': False} })
                        apiResultsTotal = -1
                    else:
                        self.log.error("Unknown 'Content-Type' response header returned: '%s'" % r.headers['Content-Type'])
                        self.log.debug("API EndPoint response: %s\n%s ", r.reason, r.text)
                        rJson = json.dumps({'result': {'success': False} })
                        apiResultsTotal = -1
                else:
                    self.log.error("Missing 'Content-Type' in API response's header")
                    self.log.debug("API EndPoint response: %s\n%s ", r.reason, r.text)
                    rJson = json.dumps({'result': {'success': False} })
                    apiResultsTotal = -1
            yield rJson


    def setRouter(self, routerName):
        '''
        Set object to specific API router.
        Basic error checking that specified router actually exisits.
        '''
        if not (routerName in self.routerEndpointMap.keys()):
            raise Exception("Specified router, '%s' is not a known API router" % routerName)
        self._url = self.config['url'] + self.getEndpoint(routerName)
        self._routerName = routerName
        return


    def getEndpoint(self, router):
        '''
        Return URL for specified API router.
        Borrowed from original zenoss_api/RouterEndpointMap.py.
        '''
        if router in self.routerEndpointMap.keys():
            return self.routerEndpointMap.get(router)
        else:
            self.log.error('Router not found')
            return ""


    def getRouterEndpointMappings(self):
        '''
        Return map of API router and its URL.
        Borrowed from original zenoss_api/RouterEndpointMap.py.
        '''
        return {'AWSRouter': '/zport/dmd/aws_router',
                'ApplicationRouter': '/zport/dmd/application_router',
                'AzureRouter': '/zport/dmd/azure_router',
                'CallhomeRouter': '/zport/dmd/callhome_router',
                'CiscoUCSRouter': '/zport/dmd/ciscoucs_router',
                'ComponentGroupRouter': '/zport/dmd/componentgroup_router',
                'DashboardRouter': '/zport/dmd/dashboard_router',
                'DetailNavRouter': '/zport/dmd/detailnav_router',
                'DeviceDumpLoadRouter': '/zport/dmd/devicedumpload_router',
                'DeviceManagementRouter': '/zport/dmd/devicemanagement_router',
                'DeviceRouter': '/zport/dmd/device_router',
                'DiagramRouter': '/zport/dmd/diagram_router',
                'DistributedCollectorRouter': '/zport/dmd/dc_router',
                'DynamicViewRouter': '/zport/dmd/dynamicservice_router',
                'ElementPoolRouter': '/zport/dmd/elementpool_router',
                'EnterpriseServicesRouter': '/zport/dmd/enterpriseservices_compat_router',
                'EtlRouter': '/zport/dmd/etl_router',
                'EventClassesRouter': '/zport/dmd/evclasses_router',
                'EventsRouter': '/zport/dmd/evconsole_router',
                'HostRouter': '/zport/dmd/host_router',
                'HyperVRouter': '/zport/dmd/hyperv_router',
                'ImpactRouter': '/zport/dmd/enterpriseservices_router',
                'InsightRouter': '/zport/dmd/insight_router',
                'IntrospectionRouter': '/zport/dmd/introspection_router',
                'JobsRouter': '/zport/dmd/jobs_router',
                'LDAPRouter': '/zport/dmd/ldap_router',
                'LicensingRouter': '/zport/dmd/licensing_router',
                'LogicalNodeRouter': '/zport/dmd/logicalnode_router',
                'ManufacturersRouter': '/zport/dmd/manufacturers_router',
                'MessagingRouter': '/zport/dmd/messaging_router',
                'MibRouter': '/zport/dmd/mib_router',
                'MonitorRouter': '/zport/dmd/monitor_router',
                'MultiRealmRouter': '/zport/dmd/multirealm_router',
                'Network6Router': '/zport/dmd/network_6_router',
                'NetworkRouter': '/zport/dmd/network_router',
                'OpenStackInfrastructureRouter': '/zport/dmd/openstackinfrastructure_router',
                'OpenStackRouter': '/zport/dmd/openstack_router',
                'ProcessRouter': '/zport/dmd/process_router',
                'PropertiesRouter': '/zport/dmd/properties_router',
                'PropertyMonitorRouter': '/zport/dmd/propertymonitor_router',
                'RelatedEventsRouter': '/zport/dmd/relatedevents_router',
                'ReportRouter': '/zport/dmd/report_router',
                'SAMLIdPRouter': '/zport/dmd/SAMLIdPRouter',
                'SearchRouter': '/zport/dmd/search_router',
                'ServiceRouter': '/zport/dmd/service_router',
                'ServiceTemplatesRouter': '/zport/dmd/servicetemplates_router',
                'SettingsRouter': '/zport/dmd/settings_router',
                'StorageBaseRouter': '/zport/dmd/storage_router',
                'SupportRouter': '/zport/dmd/support_router',
                'TemplateRouter': '/zport/dmd/template_router',
                'TriggersRouter': '/zport/dmd/triggers_router',
                'UsersRouter': '/zport/dmd/users_router',
                'VCloudRouter': '/zport/dmd/vcloud_router',
                'ZenPackRouter': '/zport/dmd/zenpack_router',
                'ZenWebTxRouter': '/zport/dmd/zenwebtx_router',
                'vSphereRouter': '/zport/dmd/vsphere_router'
                }


# Get HTML page title. Used when 'text/html' Content-Type is returned
# Borrowed from:
# https://stackoverflow.com/questions/51233/how-can-i-retrieve-the-page-title-of-a-webpage-using-python/36650753#36650753
class TitleParser(HTMLParser):
    '''
    Parse HTML text and return HTML Title
    '''
    def __init__(self):
        HTMLParser.__init__(self)
        self.match = False
        self.title = ''

    def handle_starttag(self, tag, attributes):
        self.match = True if tag == 'title' else False

    def handle_data(self, data):
        if self.match:
            self.title = data
            self.match = False
                
def log2stdout(loglevel):
    '''
    Setup logging
    '''
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(loglevel)
    return logging.getLogger('zenApiLib')

if __name__ == '__main__':
    log = log2stdout(logging.INFO)
    # Some examples
    # API call: {"action":"DeviceRouter","method":"getDevices", "data": [ {"keys": ["productionState"], "params": {"productionState": [1000]},  "limit": 1, "start": 0} ], "tid":1}
    print "DeviceRouter: getDevices"
    zenAPI = ZenAPIConnector()
    zenAPI.setRouter('DeviceRouter')
    print list(zenAPI.callMethod(
        'getDevices',
        keys = ["productionState"],
        params = {
            "productionState": [1000]
        }
    ))
    # API Call: {"action":"TriggersRouter","method":"getTriggers","data":[], "tid":1}
    print "TriggerRouter: getTriggers"
    triggerAPI = ZenAPIConnector(routerName = 'TriggersRouter')
    for i in triggerAPI.callMethod("getTriggers"):
        print i
