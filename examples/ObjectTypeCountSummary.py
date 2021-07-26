import sys
import zenApiLib
from pprint import pformat

import argparse
import sys
import logging


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
    return parser.parse_args()


if __name__ == '__main__':
    args = vars(buildArgs())
    log, rOut = initScriptEnv(args)

    apiSearchRouter = zenApiLib.zenConnector(
        section=args['configSection'],
        cfgFilePath=args['configFilePath'],
        routerName='SearchRouter'
    )
    apiResponse = apiSearchRouter.callMethod('getCategoryCounts', query='*')
    if apiResponse['result'].get('total'):
        log.info(pformat(apiResponse['result']['results']))
        log.info('Total: %s', apiResponse['result']['total'])
    else:
        log.error('Issue making API call, %r', apiResponse)