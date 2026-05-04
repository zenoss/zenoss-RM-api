#!/usr/bin/env python
"""
zenApiLib - Zenoss Resource Manager API Library
Compatible with Python 2.7 and Python 3.6+
"""
from __future__ import print_function, absolute_import

import os
import json
import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import six
from six.moves.configparser import ConfigParser
from six.moves.http_client import HTTPConnection
from six.moves.html_parser import HTMLParser

if not ('logging' in dir()):
    import logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)


class zenConnector(object):
    '''
    Enhanced API library embedding increased functionality & error handling
    '''
    def __init__(self, section='default', cfgFilePath='', routerName=None, loglevel=40):
        self._url = ''
        self._routerName = ''
        self._routersInfo = {}
        self._apiResultsRaw = False
        self.configSectionName = section
        self._tid = 0
        self.log = logging.getLogger('zenApiLib.ZenConnector')
        self.log.setLevel(loglevel)
        self.config = self._getConfigDetails(section, cfgFilePath)
        self.requestSession = self.getRequestSession()
        if not routerName:
            self.setRouter('IntrospectionRouter')
        else:
            self.setRouter(routerName)

    def _getConfigDetails(self, section, cfgFilePath):
        '''
        Read 'creds.cfg' configuration file. Default location being in the
        same directory as the python library file & return parameters in
        specific 'section'.
        '''
        if isinstance(cfgFilePath, dict):
            return self._sanitizeConfig(cfgFilePath)
        self.log.info('_getConfigDetails; section:%s, cfgFilePath:%s' % (section, cfgFilePath))
        configurations = ConfigParser()
        if cfgFilePath == '':
            cfgFilePath = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__), 'creds.cfg')
            )
        configurations.read(cfgFilePath)
        if not (section in configurations.sections()):
            raise Exception('Specified configuration section, "%s" not defined in "%s".' % (section, cfgFilePath))
        configuration = dict(configurations.items(section))
        return self._sanitizeConfig(configuration)

    def _sanitizeConfig(self, configuration):
        '''
        Ensure 'creds.cfg' configuration file has required fields.
        Deal with special fields.
        '''
        self.log.info('_sanitizeConfig; configuration:%s' % (configuration))
        if not ('url' in configuration):
            raise Exception('Configuration file missing "url" key')
        if 'cz' in configuration:
            if 'apikey' not in configuration:
                raise Exception('Configuration file missing "apikey" key')
            configuration['url'] = '{}/{}'.format(configuration['url'], configuration['cz'])
        elif 'username' in configuration:
            if 'password' not in configuration:
                self.log.error('Configuration file missing "password" key')
        else:
            raise Exception('Configuration missing username or collection zone prefix')
        if 'timeout' not in configuration:
            configuration['timeout'] = 3
        else:
            configuration['timeout'] = float(configuration['timeout'])
        if 'retries' not in configuration:
            configuration['retries'] = 3
        else:
            configuration['retries'] = float(configuration['retries'])
        sslVerify = True
        if 'ssl_verify' in configuration:
            if configuration['ssl_verify'].lower() == 'false':
                sslVerify = False
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        configuration['ssl_verify'] = sslVerify
        disableSaml = False
        if 'disable_saml' in configuration:
            if configuration['disable_saml'].lower() == 'true':
                disableSaml = True
        configuration['disable_saml'] = disableSaml
        return configuration

    def getRequestSession(self):
        '''
        Setup defaults for using the requests library
        '''
        self.log.info('getRequestSession;')
        s = requests.Session()
        retries = Retry(
            total=self.config['retries'],
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504, 405]
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))
        s.mount('http://', HTTPAdapter(max_retries=retries))
        return s

    def callMethod(self, *method, **payload):
        '''
        Call API directly and returns results directly. For paging API calls
        use self.pagingMethodCall.
        NOTE: There are two methods to pass the method parameters:
          preferred: self.callMethod('getDevices', uid="/zport/dmd/Devices", keys=["name","ipAddress"])
           override: self.callMethod('getDevices', override={"data": {"uid":"/zport/dmd/Devices","keys":["name","ipAddress"]}})
        '''
        self.log.info('callMethod; method:%s, payload:%s' % (method, payload))
        if self._routerName != 'IntrospectionRouter':
            if not (method[0] in self._routersInfo[self._routerName]['methods'].keys()):
                raise Exception("Specified router method '%s' is not an option. Available methods for '%s' router are: %s" % (
                    method[0],
                    self._routerName,
                    sorted(self._routersInfo[self._routerName]['methods'].keys())
                ))
        if self.log.getEffectiveLevel() == 10:
            HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger('requests.packages.urllib3')
        requests_log.setLevel(self.log.getEffectiveLevel())
        requests_log.propagate = True
        self._tid += 1
        apiBody = {
            'action': self._routerName,
            'method': method[0],
            'tid': self._tid,
        }
        if len(payload) == 1 and 'override' in payload:
            apiBody.update(payload['override'])
        else:
            apiBody['data'] = [payload]
        try:
            if 'cz' in self.config:
                r = self.requestSession.post(
                    self._url,
                    verify=self.config['ssl_verify'],
                    timeout=self.config['timeout'],
                    headers={
                        'content-type': 'application/json',
                        'z-api-key': self.config['apikey'],
                    },
                    data=json.dumps(apiBody),
                )
            else:
                r = self.requestSession.post(
                    self._url,
                    auth=(self.config['username'], self.config['password']),
                    verify=self.config['ssl_verify'],
                    timeout=self.config['timeout'],
                    headers={'content-type': 'application/json'},
                    data=json.dumps(apiBody),
                )
        except Exception as e:
            msg = 'Requests exception: %s' % e
            self.log.error(msg)
            return {'result': {'success': False}, 'msg': msg}
        if self._apiResultsRaw:
            return r
        return self._validateRawResponse(r)

    def pagingMethodCall(self, *method, **payload):
        '''
        Returns an iterative, generator type object of API call results.
        Queries that return a large # of results (>50, default) will be broken
        up into entries. Note not all API router method calls support splitting
        up large results into manageable chunks (e.g. getDevices vs. getTriggers)
        '''
        self.log.info('pagingMethodCall; method:%s, payload:%s' % (method, payload))
        apiResultsReturned = 0
        apiResultsTotal = 1
        limitApiCallResults = 100
        if 'start' in payload:
            apiResultsReturned = payload['start']
        if 'limit' in payload:
            limitApiCallResults = payload['limit']
        else:
            payload['limit'] = limitApiCallResults
        while apiResultsReturned < apiResultsTotal:
            self.log.info('pagingMethodCall: tid:%s, start:%s, limit:%s, estimatedTotal:%s' % (
                self._tid, apiResultsReturned, limitApiCallResults, apiResultsTotal))
            rJson = self.callMethod(method[0], **payload)
            if 'totalCount' in rJson['result']:
                apiResultsTotal = rJson['result']['totalCount']
            elif 'total' in rJson['result']:
                apiResultsTotal = rJson['result']['total']
            else:
                apiResultsTotal = -1
            if apiResultsTotal != -1:
                if 'start' in payload:
                    apiResultsReturned = payload['start'] + limitApiCallResults
                    payload['start'] += limitApiCallResults
                else:
                    apiResultsReturned = limitApiCallResults
                    payload['start'] = limitApiCallResults
            yield rJson

    def _validateRawResponse(self, r):
        '''
        Validate and parse raw requests Response into result dict.
        '''
        self.log.info("_validateRawResponse: passed object type of '%s'" % type(r))
        if r.status_code != 200:
            self.log.error("API call returned a '%s' http status." % r.status_code)
            self.log.debug("API EndPoint response: %s\n%s", r.reason, r.text)
            return {'result': {'success': False}}
        if 'Content-Type' in r.headers:
            if 'application/json' in r.headers['Content-Type']:
                rJson = r.json()
                self.log.debug('_validateRawResponse: Response returned:\n%s' % rJson)
                return rJson
            elif 'text/html' in r.headers['Content-Type']:
                parser = TitleParser()
                parser.feed(r.text)
                msg = "HTML response from API call. HTML page title: '%s'" % parser.title
                self.log.error(msg)
                self.log.debug("API EndPoint response: %s\n%s", r.reason, r.text)
                return {'result': {'success': False}, 'msg': msg}
            else:
                msg = "Unknown 'Content-Type' response header returned: '%s'" % r.headers['Content-Type']
                self.log.error(msg)
                self.log.debug("API EndPoint response: %s\n%s", r.reason, r.text)
                return {'result': {'success': False}, 'msg': msg}
        else:
            msg = "Missing 'Content-Type' in API response's header"
            self.log.error(msg)
            self.log.debug("API EndPoint response: %s\n%s", r.reason, r.text)
            return {'result': {'success': False}, 'msg': msg}

    def setRouter(self, routerName):
        '''
        Set object to specific API router.
        Basic error checking that specified router actually exists.
        '''
        self.log.info('setRouter: routerName:%s' % (routerName))
        routers = {}
        self._routerName = 'IntrospectionRouter'
        self._url = self.config['url'] + self._getEndpoint('IntrospectionRouter')
        if self.config['disable_saml']:
            self._url += '?saml=0'
        if self._routersInfo == {}:
            apiResp = self.callMethod('getAllRouters')
            if not apiResp['result']['success']:
                raise Exception('getAllRouters call was not successful')
            if not len(apiResp['result']['data']) > 0:
                raise Exception('getAllRouters call did not return any results')
            for resp in apiResp['result']['data']:
                routerKey = resp.get('action', 'unknown')
                routers[routerKey] = resp
                routers[routerKey]['methods'] = {}
            self._routersInfo = dict(routers)
        if routerName not in self._routersInfo.keys():
            raise Exception("Specified router '%s' is not an option. Available routers are: %s" % (
                routerName, sorted(self._routersInfo.keys())
            ))
        if self._routersInfo[routerName]['methods'] == {}:
            apiResp = self.callMethod('getRouterMethods', router=routerName)
            if not apiResp['result']['success']:
                raise Exception('getRouterMethods call was not successful')
            if not len(apiResp['result']['data']) > 0:
                raise Exception('getRouterMethods call did not return any results')
            self._routersInfo[routerName]['methods'] = dict(apiResp['result']['data'])
        self._routerName = routerName
        self._url = self.config['url'] + self._getEndpoint(routerName)
        if self.config['disable_saml']:
            self._url += '?saml=0'

    def _getEndpoint(self, routerName):
        '''
        Return URL for specified API router.
        '''
        self.log.info('_getEndpoint: router:%s' % (routerName))
        if routerName in self._routersInfo.keys():
            return self._routersInfo[routerName]['urlpath']
        elif routerName == 'IntrospectionRouter':
            return '/zport/dmd/introspection_router'
        else:
            self.log.error('Router not found')
            return ''


class ZenAPIConnector(zenConnector):
    '''
    Backwards compatibility for zenoss_api/ZenAPIConnector.py
    '''
    def __init__(self, router, method, data):
        self._url = ''
        self._routerName = ''
        self._routersInfo = {}
        self._apiResultsRaw = False
        self._tid = 0
        self.log = logging.getLogger('zenApiLib.ZenAPIConnector')
        self.log.warning('This is a backwards compatibility adapter.')
        print('WARN: This is a backwards compatibility adapter.')
        self.config = self._getConfigDetails('default', '')
        self.requestSession = self.getRequestSession()
        self.setRouter(router)
        self.method = method
        self.data = data

    def send(self):
        self._apiResultsRaw = True
        return self.callMethod(self.method, **self.data)


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


if __name__ == '__main__':
    print("For help reference the README.md file")
    print("If you are trying to make a command line call to the API, all command line invocations functions have been moved to zenApiCli.py")
