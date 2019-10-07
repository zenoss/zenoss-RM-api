#!/usr/bin/env python
#####################################################
# This script is a basic example of how to query    #
# the event console using the json api using the    #
# Zenoss JSON API and the ZenAPIConnector class     #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

import zenApiLib
import sys
import json
import argparse

def get_args():
    parser = argparse.ArgumentParser(
        """Utility to search the Event Console through cli.

        Example component search field:

            --component "eth0"

        Example DeviceClass search field:

            --deviceclass "/Server/SSH/Linux"

        Example EventClass search field:

            --eventclass "/Cmd/Fail"
        
        Example EventState search field:

            Defaults to: 01 (New, Acknowledged)
            For example, to filter on eventstates
            of Closed and Cleared, you would use 
            the following:

            --eventstate 34 

            Possible values in list:

                "0 = New"
                "1 = Acknowledged"
                "2 = Suppressed"
                "3 = Closed"
                "4 - Cleared"
                "5 = Dropped"
                "6 = Aged"
        
        Example severity search field:

            Defaults to: 5432 (Critical, Error, etc)
            For example, to filter on Critical
            and Error severity events:

            --severity 54

            Possible values in list:

                "5 = Critical;"
                "4 = Error;"
                "3 = Warning;"
                "2 = Info;"
                "1 = Debug;"
                "0 = Clear"

        Example Summary search field:
        
            --summary "SSH*"
        """
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Specify a component pattern filter",
    )
    parser.add_argument(
        "--count",
        type=int,
        help="The total count of events to retrieve",
    )
    parser.add_argument(
        "--device",
        type=str,
        help="Specify a Device patter filter",
    )
    parser.add_argument(
        "--deviceclass",
        type=str,
        help="Specify a DeviceClass pattern filter",
    )
    parser.add_argument(
        "--eventkey",
        type=str,
        help="Specify an eventKey pattern filter",
    )
    parser.add_argument(
        "--eventclasskey",
        type=str,
        help="Specify an eventClassKey patter filter",
    )
    parser.add_argument(
        "--eventclass",
        type=str,
        help="Specify an eventClass pattern filter",
    )
    parser.add_argument(
        "--eventstate",
        default="[0, 1]",
        help="Specify an eventState pattern filter",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max index of events to retrieve.  defaults to 100.",
    )
    parser.add_argument(
        "--severity",
        default="[5, 4, 3, 2]",
        help="Specify the severity to filter",
    )
    parser.add_argument(
        "--summary",
        type=str,
        help="The event summary to search for",
    )

    args = parser.parse_args()
    return(args)


def makeQuery(data, count):
    """limit is defined as Max index of events to retrieve (default: 0)
    start is defined as Min index of events to retrieve (default: 0)
    Example api method call pulled from developer tools in chrome
    and filtering on 'evconsole_router'.
    For example, the following request was made when browsing the
    event console in chrome:

    {'action': 'EventsRouter',
    'data': [{'dir': 'ASC',
            'keys': ['eventState',
                        'severity',
                        'eventClass',
                        'DeviceClass',
                        'device',
                        'component',
                        'summary',
                        'firstTime',
                        'lastTime',
                        'count',
                        'evid',
                        'eventClassKey',
                        'message'],
            'limit': 200,
            'page': 4,
            'params': {'eventState': [0, 1],
                        'excludeNonActionables': False,
                        'severity': [5, 4, 3, 2],
                        'tags': []},
            'sort': 'eventClass',
            'start': 600,
            'uid': '/zport/dmd'}],
    'method': 'query',
    'tid': 34,
    'type': 'rpc'}

    strange evconsole query behavior observed:
    if count is less than limit, the query will return the same number
    of events as there are limits.  Otherwise, count will be used to
    pull the count number of events.  To work around this, we are
    setting the value of limit to the value of count.
    """
    if count:
        count = count
    else:
        results = api.callMethod('query', **data)
        count = results.get('result').get('totalCount')

    if count < data.get('limit'):
        data['limit'] = count
        results = api.callMethod('query', **data)
        if results:
            yield results
    else:
        while data.get('start') < count:
            try:
                if (count - data.get('start')) < data.get('limit'):
                    data['limit'] = count - data.get('start')
                    data['page'] += 1

                results = api.callMethod('query', **data)
                yield results

                data['start'] += data.get('limit')
                data['page'] += 1

            except Exception as ex:
                print(ex)


def extractEvents(results):
    try:
        events = results['result']['events']
    except:
        events = dict(events=None)
        print("No events returned from query")
    return events


if __name__ == '__main__':
    opts = get_args()
    component = opts.component
    count = opts.count
    device = opts.device
    deviceClass = opts.deviceclass
    eventKey = opts.eventkey
    eventClassKey = opts.eventclasskey
    eventClass = opts.eventclass
    eventState = eval(opts.eventstate)
    limit = opts.limit
    severity = eval(opts.severity)
    summary = opts.summary
    start = 0
    page = 1

    # Build params dictionary and keys list for data dictionary

    data = dict()
    params = dict()

    if component:
        params.update(component = component)
    if device:
        params.update(device = device)
    if deviceClass:
        params.update(DeviceClass = deviceClass)
    if eventKey:
        params.update(eventKey = eventKey)
    if eventClassKey:
        params.update(eventClassKey = eventClassKey)
    if eventClass:
        params.update(eventClass = eventClass)
    if eventState:
        params.update(eventState = eventState)
    if limit:
        data.update(limit = limit)
    if severity:
        params.update(severity = severity)
    if summary:
        params.update(summary = summary)
    data.update(start = start)
    data.update(page = page)

    keys = [
        'eventState',
        'severity',
        'eventClass',
        'eventClassKey',
        'eventKey',
        'DeviceClass',
        'device',
        'component',
        'summary',
        'firstTime',
        'lastTime',
        'count',
        'evid',
        'message'
        ]

    data.update(params = params)
    data.update(keys = keys)

    api = zenApiLib.zenConnector(routerName = 'EventsRouter')


    results = makeQuery(data, count)

    for result in results:
        print((json.dumps(extractEvents(result))))

