#!/bin/env python
# Clear Heartbeats
import zenApiLib
import argparse
import sys
import logging
from pprint import pformat

def buildArgs():
    parser = argparse.ArgumentParser(description='Clear Heatbeats',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', dest='loglevel', action='store', type=int,
                        default=30, help='Set script logging level (DEBUG=10,'
                        ' INFO=20, *WARN=30, ERROR=40, CRTITICAL=50')
    parser.add_argument('-p', dest='configFilePath', action='store',
                        metavar="credsFilePath", default='', help='Default '
                        'location being the same directory as the zenApiLib.py'
                        'file')
    parser.add_argument('-c', dest='configSection', action='store',
                        default='default',
                        help='zenApiLib credential configuration section')
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    args = vars(buildArgs())
    logging.getLogger().setLevel(args['loglevel'])
    log = logging.getLogger(__file__)
    log.setLevel(args['loglevel'])
    api = zenApiLib.zenConnector(
                    routerName='EventsRouter',
                    cfgFilePath=args['configFilePath'],
                    section=args['configSection'],
                    loglevel=args['loglevel'])
    if api.config['timeout'] < 30:
        api.config['timeout'] = 30
    rOut = sys.stdout

    apiRawResult = api.callMethod('clear_heartbeats')

    if not apiRawResult.get('success', True):
        log.error('Issue clearing heartbeats\n{}'.format(pformat(apiRawResult)))
        sys.exit(1)
    else:
        log.info('Successfully cleared heartbeats\n{}'.format(pformat(apiRawResult)))

    sys.exit(0)
