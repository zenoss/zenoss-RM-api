#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of jobs and display job-related info using   #
# the Zenoss JSON API and the ZenAPIConnector class #
# written by Adam McCurdy @ Zenoss                  #
#####################################################
from __future__ import print_function

import zenApiLib

import time
import datetime

router = 'JobsRouter'
method = 'getJobs'
data = {'start': 0,
        'sort': 'started',
        'limit': 200,
        'page': 0,
        'dir': 'DESC'}

# referenced from celery.status.py
unfinished_jobs = [
    'PENDING',
    'RECEIVED',
    'STARTED',
    'RETRY'
]


def getJobs():
    '''
    This makes the API call and returns data
    '''
    dr = zenApiLib.zenConnector(routerName = router)
    response = dr.callMethod(method, **data)
    if response.get('result', {}).get('success', False) is False:
        raise Exception('API call returned unsucessful result.\n%s' % response)
    return response['result']


def r_time(time):
    n_time = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    return n_time


def longRunning(jobs):
    '''
    Setting a recommended default of 6 hours(21600 seconds)
    for long running jobs
    '''
    now = time.time()
    l_jobs = []
    for job in jobs['jobs']:
        if any(job['status'] == s for s in unfinished_jobs):
            if not job['finished']:
                if now - job['scheduled'] > 21600:
                    l_jobs.append(job)
    return(l_jobs)


def jobReport():
    jobs = getJobs()
    l_jobs = longRunning(jobs)
    if not l_jobs:
        print('No long running jobs found.')
    else:
        print('ScheduledTime, Status, Description, Started, UUID, '\
            'User, Type')
        for job in l_jobs:
                scheduled = r_time(job['scheduled'])
                status = job['status']
                description = job['description']
                started = job['started']
                uuid = job['uuid']
                user = job['user']
                jobtype = job['type']
                print('%s, %s, %s, %s, %s, %s, %s' % (scheduled,
                                                        status,
                                                        description,
                                                        started,
                                                        uuid,
                                                        user,
                                                        jobtype))


if __name__ == '__main__':
    jobReport()
