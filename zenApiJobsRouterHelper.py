import zenApiLib
import logging
from time import time, sleep

if not ('logging' in dir()):
    import logging
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)

api = zenApiLib.zenConnector(section = 'default', routerName = 'JobsRouter')

def checkJobStatus(jobid):
    result = api.callMethod('getInfo', jobid=jobid)
    try:
        status = result['result']['data']['status']
    except (KeyError, ValueError):
        status = 'UNKNOWN! Invalid Job ID or other failure'
    return status

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
    if jobStatus == 'FAILURE':
        return jobStatus, False
    elif jobStatus == 'ABORTED':
        return jobStatus, False
    elif jobStatus == 'TIMEOUT':
        return jobStatus, False
    elif jobStatus == 'SUCCESS':
        return jobStatus, True