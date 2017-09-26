#!/usr/bin/env python
#####################################################
# This script is a basic example of how to create a #
# list of jobs and display job-related info using   #
# the Zenoss JSON API and the ZenAPIConnector class #
# written by Adam McCurdy @ Zenoss                  #
#####################################################

from ZenAPIConnector import ZenAPIConnector

router = 'JobsRouter'
method = 'getJobs'
data = {'start': 0,
        'sort': 'started',
        'limit': 200,
        'page': 0,
        'dir': 'DESC'}


def getJobs():
    '''
    This makes the API call and returns data
    '''
    api = ZenAPIConnector(router, method, data)
    response = api.send()
    resp_data = response.json()['result']
    return resp_data


def jobReport():
    jobs = getJobs()
    print 'Scheduled, Status, Description, Started, UUID, '\
          'Finished, User, Type'
    for job in jobs['jobs']:
        scheduled = job['scheduled']
        status = job['status']
        description = job['description']
        started = job['started']
        uuid = job['uuid']
        finished = job['finished']
        user = job['user']
        jobtype = job['type']
        print '%s, %s, %s, %s, %s, %s, %s, %s' % (scheduled,
                                                  status,
                                                  description,
                                                  started,
                                                  uuid,
                                                  finished,
                                                  user,
                                                  jobtype)


if __name__ == '__main__':
    jobReport()
