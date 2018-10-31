import zenApiLib
import logging

if not ('logging' in dir()):
    import logging
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.getLogger().setLevel(logging.ERROR)


class zenApiJobsRouterHelper():
    def __init__(self, debug=False):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        self.api = zenApiLib.zenConnector(section = 'default', routerName = 'JobsRouter')
        self.log = logging.getLogger(self.__class__.__name__)

    def checkJobStatus(self, jobid):
        result = self.api.callMethod('getInfo', jobid=jobid)
        try:
            status = result.json()['result']['data']['status']
        except (KeyError, ValueError):
            status = 'UNKNOWN! Invalid Job ID or other failure'
        return status

    def watchStatus(self, jobid, timeout=300):
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
            jobStatus = self.checkJobStatus(jobid)
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