import argparse
import json
import logging
import re
import sys
from pprint import pformat
import zenApiLib

filterPattern = None
sourceObject = None
destinObject = None
counters = {}
DESTIN_UID_PLUGINS = []


# Example UID Destin plugin. If Destin UID is different than Source.
# In most cases should not be needed, try to avoid needing a plugin.
# def _uidDeviceIdAllLowerCase(uid):
#     """
#     Example Destin UID plugin. Use case, source DeviceName is Uppercase and destination is
#     lowercase.
#     """
#     m = re.match("(.*/devices)/([a-zA-Z0-9-_.]+)/(.*)", uid)
#     if m:
#         return "{}/{}/{}".format(m.group(1), m.group(2).lower(), m.group(3))
#     return None
# Then added the method to the list of plugins to try. First plugin to find an object on the 
# destination will be used.
# DESTIN_UID_PLUGINS.append(_uidDeviceIdAllLowerCase)


def getDefaultScriptArgParser():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, WARN=30, ERROR=40, CRTITICAL=50)')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-c', dest='configSection', action='store',
                        metavar="credsSection", default='default',
                        help='zenApiLib credential configuration section '
                        '(default)')
    parser.add_argument('-o', dest='outFileName', action='store', default=None,
                        help="Output to file instead of stdout.")

    return parser


def initScriptEnv(args):
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    if args['outFileName']:
        rOut = open(args['outFileName'], 'w')
    else:
        rOut = sys.stdout

    return log, rOut


def buildArgs():
    parser = getDefaultScriptArgParser()
    # Change default logging value. Logging arg is position 1
    parser._actions[1].default = 20
    #
    parser.description = 'Component attribute sync'
    parser.add_argument('-s', dest='sourceZ', action='store', required=True,
                        help='Zenoss instance credential section to be used as the source or if '
                             'starts with "file:" the file to use for Object Uid & attribute '
                             'values')
    parser.add_argument('-d', dest='destinationZ', action='store', required=True,
                        help='Zenoss instance credential section to be used as the destination or '
                             'if starts with "file:" the file to use to dump Object Uids & '
                             'attribute values')
    parser.add_argument('-t', dest='metaTypes', action='append', required=True,
                        help='Object type to search for. Can be defined multiple times')
    parser.add_argument('-a', dest='attributes', action='append', required=True,
                        help='Object attributes to compare & update. Can be defined multiple times')
    parser.add_argument('-x', dest='dryRun', action='store_true', required=False,
                        help='Do not make change on Destination')
    parser.add_argument('-f', dest='filterUid', action='store', required=False, default='',
                        help='Filter to use on Zenoss object uid')
    parser.add_argument('-ss', dest='sourceStart', action='store', required=False, default=0,
                        type=int, help='From source, start at')
    parser.add_argument('-se', dest='sourceEnd', action='store', required=False, default=0,
                        type=int, help='From source, end at')
    return parser.parse_args()


def _initIOObject(argValue, name):
    global sourceObject
    if 'file:' in argValue:
        filename = argValue.split(':')[1]
        if name == "Source":
            log.warn('"-t" command parameter does not apply when source is a file')
            ioObject = json.load(open(filename, 'r'))
            count('Total objects in "{}" Source file'.format(filename), len(ioObject))
            if args['sourceStart'] or args['sourceEnd']:
                ioObject = _batchWindowSlice(ioObject, args['sourceStart'], args['sourceEnd'])
        elif name == "Destination":
            ioObject = open(filename, 'w')
    else:
        try:
            ioObject = zenApiLib.zenConnector(section=argValue)
        except Exception as e:
            log.error('Issue communicating with %s Instance API\n%r', name, e)
            sys.exit(1)
    return ioObject


def _batchWindowSlice(object, start, end):
    if end != 0:
        object = object[:end]
        count('"Batch" window end at object', end)
    if start != 0:
        object = object[start:]
        count('"Batch" window start at object', start)
    count('"Batch" window Total objects', len(object))
    return object


def _searchrouterGetResults(oAPI, metaTypes):
    oAPI.setRouter('SearchRouter')
    searchResults = []
    for apiResponse in oAPI.pagingMethodCall('getAllResults', query='*', category=metaTypes):
        if not apiResponse['result'].get('total'):
            raise Exception('search_router getAllResults method call non-successful: %r', apiResponse)
        else:
            # extract uid (some reason it is keyed 'url') from search results
            searchResults.extend([x['url'] for x in apiResponse['result']['results']])
    count('API Searched "{}" objects found on Source'.format(metaTypes), len(searchResults))
    if args['sourceStart'] or args['sourceEnd']:
        searchResults = _batchWindowSlice(searchResults, args['sourceStart'], args['sourceEnd'])
    return searchResults


def _devrouterUidAttrValues(oAPI, uid, attrNames):
    oAPI.setRouter('DeviceRouter')
    apiResponse = oAPI.callMethod(
        'getInfo',
        uid=uid,
        keys=attrNames
    )
    if 'result' not in apiResponse:
        log.error('device_router getInfo return unexpected API format: %r', apiResponse)
        return None
    elif 'success' in apiResponse['result'] and apiResponse['result']['success'] is False:
        if 'msg' in apiResponse['result'] and 'ObjectNotFoundException' in apiResponse['result']['msg']:
            return None
        elif 'msg' in apiResponse['result'] and 'Could not adapt' in apiResponse['result']['msg'] and \
                'Relationship at' in apiResponse['result']['msg']:
            # Sometimes ObjectIds are the same as a relname on the object. If UID does not exist a
            # red-herring error message will be thrown like
            # "TypeError: ('Could not adapt', &lt;ToManyContRelationship at"
            return None
        else:
            log.error('device_router getInfo method call non-successful: %r', apiResponse)
            return None
    elif 'success' in apiResponse['result'] and apiResponse['result']['success'] is True:
        result = apiResponse['result']['data']
        return result
    else:
        log.error('device_router getInfo method call majorly unsuccessful: %r', apiResponse)
        return None


def _devrouterUidSetInfo(oAPI, uid, data):
    oAPI.setRouter('DeviceRouter')
    data['uid'] = uid
    apiResponse = oAPI.callMethod('setInfo', **data)
    if not apiResponse['result']['success']:
        log.error('device_router setInfo method call non-successful: %r', apiResponse)


def _devrouterLockComponents(oAPI, uid, lockData):
    oAPI.setRouter('DeviceRouter')
    # Massage data from getInfo() into format lockComponents() takes
    lockData['uids'] = [uid]
    lockData['sendEvent'] = lockData['events']
    del lockData['events']
    # hashcheck is needed, otherwise: "TypeError: lockComponents() takes at least 3 arguments"
    lockData['hashcheck'] = None
    apiResponse = oAPI.callMethod(
        'lockComponents',
        **lockData
    )
    if not apiResponse['result']['success']:
        log.error('device_router lockComponents method call non-successful: %r', apiResponse)


def iterGetSourceX():
    # If Source is API, return Source UID
    # If Source is file, return source Values
    if args['filterUid']:
        filterPattern = re.compile(args['filterUid'])
    if isinstance(sourceObject, list):
        # Warn if specified attributes are missing from file
        if sourceObject and set(args['attributes']).issubset(sourceObject[0].keys()) is False:
            log.error('Not all specified attributes "%r" are in the file "%r"',
                      args['attributes'],
                      sourceObject[0].keys())
            sys.exit(1)

        for sourceValues in sourceObject:
            if not isinstance(sourceValues, dict):
                log.error('Bad Entry in file, value is "%r"', sourceValues)
                continue
            uid = sourceValues['uid']
            if args['filterUid'] and not filterPattern.match(uid):
                count('Source objects excluded by filter')
                continue
            yield sourceValues
    else:
        for uid in _searchrouterGetResults(sourceObject, args['metaTypes']):
            if args['filterUid'] and not filterPattern.match(uid):
                count('Source objects excluded by filter')
                continue
            yield uid


def getDestinUidValues(uid):
    global destinObject, log
    if isinstance(destinObject, file):
        return True
    # Specific use-case, where destin deviceIDs became lowercase....
    destinValues = _devrouterUidAttrValues(destinObject, uid, args['attributes'])
    # Ideally component UID is identical between Zenoss instances
    # Sometimes..  that is not the case, should be a last resort... try to avoid...
    if destinValues is None:
        for uidPlugin in DESTIN_UID_PLUGINS:
            destinUid = uidPlugin(uid)
            if destinUid:
                destinValues = _devrouterUidAttrValues(destinObject, destinUid, args['attributes'])
                if destinValues:
                    log.debug('Found destination object, but had to use plugin: "%s"'
                              ' for source "%s"', uidPlugin.__name__, uid)
                    break
    return destinValues


def getSourceUidValues(uid):
    global destinObject, log
    # Should never get called when Source is a file
    return _devrouterUidAttrValues(sourceObject, uid, args['attributes'])


def writeSourceToFile():
    sourceData = []
    for uid in iterGetSourceX():
        sourceValues = getSourceUidValues(uid)
        if sourceValues and isinstance(sourceValues, dict):
            sourceData.append(sourceValues)
        else:
            log.error('Bad Entry returned from API, entry value of "%r"', sourceValues)
    json.dump(sourceData, destinObject, indent=1)
    destinObject.close()
    count('Written to file {}'.format(args['destinationZ']), len(sourceData))


def compareAndSync():
    for data in iterGetSourceX():
        if isinstance(data, (str, unicode)):
            uid = str(data)
        elif isinstance(data, dict):
            uid = data['uid']
        else:
            log.error("Data is an unknown type, %s - %r", type(data).__name__, data)
        destinValues = getDestinUidValues(uid)
        if destinValues is None:
            count('Source objects that did not exist on Destination')
            log.debug('Does not exist on destination instances: "%s"', uid)
            continue
        if isinstance(data, (str, unicode)):
            sourceValues = getSourceUidValues(uid)
        elif isinstance(data, dict):
            sourceValues = data
        if sourceValues is None:
            # Should not happen, but it did once...
            log.error('Does not exist on source instance: "%s". This should not happen and implies '
                      'something is not right.', uid)
            continue
        # Sometimes the UID will be different between source/destin, see getDestinUidValues()
        # Also, should get the 'uid' attribute out of the Values dicts
        sourceUID = sourceValues.pop('uid')
        destinUID = destinValues.pop('uid')

        # if source is a file, file could have more attributes than specified in args. extract
        # only the attributes specified in arg.
        if isinstance(sourceObject, list):
            sourceValues = {k: sourceValues[k] for k in args['attributes']}

        if sourceValues == destinValues:
            log.debug('Values match."%s"', uid)
            count('Destination objects matching Source(no change made)')
        else:
            log.info('Object synced: "%s"', destinUID)
            log.debug('%s SOURCE:%r -- DESTIN:%r', destinUID, sourceValues, destinValues)
            if args['dryRun'] is False:
                # Update Special Attributes
                if 'locking' in sourceValues:
                    _devrouterLockComponents(destinObject, destinUID, sourceValues['locking'].copy())
                    del sourceValues['locking']
                # Update General Attributes
                _devrouterUidSetInfo(destinObject, destinUID, sourceValues)
            count('Destination objects updated')


def count(name, value=None):
    if name not in counters:
        counters[name] = value if value else 1
    else:
        counters[name] += value if value else 1


if __name__ == '__main__':
    args = vars(buildArgs())
    log, rOut = initScriptEnv(args)
    log.info('Start')

    if args['dryRun']:
        log.info('DRY RUN updates will not be made to Destination, output forced into debug')
        log.setLevel(10)

    sourceObject = _initIOObject(args['sourceZ'], 'Source')
    destinObject = _initIOObject(args['destinationZ'], 'Destination')

    if isinstance(destinObject, file):
        writeSourceToFile()
    else:
        compareAndSync()

    log.info('Summary:\n' + pformat(counters, indent=1))
