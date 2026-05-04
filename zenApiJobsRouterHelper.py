#!/usr/bin/env python
"""
zenApiJobsRouterHelper - Convenience helpers for the Zenoss JobsRouter API.
Compatible with Python 2.7 and Python 3.6+
"""
from __future__ import print_function, absolute_import

import logging
from time import time, sleep

import zenApiLib

if not ('logging' in dir()):
    import logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)

_api = None


def _get_api():
    global _api
    if _api is None:
        _api = zenApiLib.zenConnector(section='default', routerName='JobsRouter')
    return _api


def checkJobStatus(jobid):
    result = _get_api().callMethod('getInfo', jobid=jobid)
    try:
        return result['result']['data']['status']
    except (KeyError, ValueError):
        return 'UNKNOWN! Invalid Job ID or other failure'


def watchStatus(jobid, timeout=300):
    '''
    This is a blocking method that will check on the status of
    a job every n seconds until it's either completed, aborted,
    failed, or a timeout is reached. It returns a tuple with the
    success status of the job, and a bool for Success or Failure
    '''
    jobStatus = 'Unknown'
    starttime = time()
    while jobStatus != 'SUCCESS':
        currtime = time()
        jobStatus = checkJobStatus(jobid)
        if starttime + timeout <= currtime:
            jobStatus = 'TIMEOUT'
            break
        elif jobStatus == 'ABORTED':
            break
        sleep(3)
    if jobStatus in ('FAILURE', 'ABORTED', 'TIMEOUT'):
        return jobStatus, False
    elif jobStatus == 'SUCCESS':
        return jobStatus, True
