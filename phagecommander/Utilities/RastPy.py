import os
import time
import requests
from bs4 import BeautifulSoup
from ruamel import yaml

RAST_URL = 'https://pubseed.theseed.org/rast/server.cgi'
RAST_USER_URL = 'https://rast.nmpdr.org/rast.cgi'


class RastException(Exception):
    pass


class RastInvalidJobError(Exception):
    pass


class RastInvalidCredentialError(Exception):
    pass


class Rast:
    """
    Class for representing queries to RAST annotation servers
    """

    def __init__(self, username: str, password: str, jobId: int = None):
        """
        Exception raised for bad authentication
        :param username:
        :param password:
        """
        self.username = username
        self.password = password
        self.file = None
        self.jobId = jobId
        self.status = None

        # authenticate user
        if not self._checkAuthentication():
            raise RastInvalidCredentialError('Invalid Credentials')

        # check for status of job if given
        if self.jobId is not None:
            self.checkIfComplete()

    def _checkAuthentication(self):
        """
        Check to see if given credentials are valid
        :return: True/False
        """
        _LOGIN_URL = 'https://rast.nmpdr.org/rast.cgi'
        args = {'page': 'Home',
                'login': self.username,
                'password': self.password,
                'action': 'perform_login'}
        checkReq = requests.post(_LOGIN_URL, data=args)
        checkReq.raise_for_status()

        # check for status of login - can be derived from <title> tag
        soup = BeautifulSoup(checkReq.content, 'html.parser')
        titleTagText = soup.find('title').text
        if 'Jobs Overview' in titleTagText:
            return True
        else:
            return False

    def submit(self, filePath: str, sequenceName: str):
        """
        Submits a file for annotation
        :param filePath: name of a fasta file
        :param sequenceName: name of the sequence
        Raises RastException if not successful
        """
        _SUBMIT_FUNCTION = 'submit_RAST_job'

        # check if file exists
        if not os.path.exists(filePath):
            raise FileNotFoundError('\"{}\" does not exist'.format(filePath))

        # attempt to submit file
        with open(filePath) as file:
            fastaContent = file.read()

        # submit args
        args = yaml.dump({'-determineFamily': 0,
                          '-domain': 'Bacteria',
                          '-filetype': 'fasta',
                          '-geneCaller': 'RAST',
                          '-geneticCode': 11,
                          '-keepGeneCalls': 0,
                          '-non_active': 0,
                          '-organismName': sequenceName,
                          '-taxonomyID': ''}, Dumper=yaml.RoundTripDumper)
        # create file content in yaml format
        file = '-file: |-\n'
        for line in fastaContent.splitlines():
            # two spaces indentation for inline string
            file += '  {}\n'.format(line)
        args += file

        payload = {'function': _SUBMIT_FUNCTION,
                   'args': args,
                   'username': self.username,
                   'password': self.password}

        submitReq = requests.post(RAST_URL, data=payload)
        submitReq.raise_for_status()

        submitResponse = yaml.safe_load(submitReq.text)
        if submitResponse['status'] == 'ok':
            self.jobId = submitResponse['job_id']
            self.status = 'incomplete'
        else:
            raise RastException('Submission: Received status response of :{}'.format(submitResponse['status']))

    def checkIfComplete(self):
        """
        Checks if the current job is complete
        Exception raised for invalid IDs
        :return: True/False
        """
        _SUCCESS_FIELD = 'status'
        _SUCCESSFUL_STATUS = 'complete'
        _CHECK_STATUS_FUNCTION = 'status_of_RAST_job'
        _ERROR_MSG_FIELD = 'error_msg'
        _ERROR_STATUS = 'error'
        _ACCESS_DENIED_ERROR = 'Access denied'
        _INVALID_JOB_ID = 'Job not found'

        if self.jobId is None:
            return False

        args = '---\n-job:\n  - {}\n'.format(self.jobId)
        payload = {'function': _CHECK_STATUS_FUNCTION,
                   'username': self.username,
                   'password': self.password,
                   'args': args}

        statusReq = requests.post(RAST_URL, data=payload)
        statusReq.raise_for_status()
        statusContent = yaml.safe_load(statusReq.text)
        jobStatus = statusContent[self.jobId][_SUCCESS_FIELD]
        self.status = jobStatus

        # raise exception for invalid jobID
        if self.status == _ERROR_STATUS:
            if statusContent[self.jobId][_ERROR_MSG_FIELD] == _ACCESS_DENIED_ERROR or _INVALID_JOB_ID:
                raise RastInvalidJobError('Invalid JobID: {}'.format(self.jobId))

        return True if jobStatus == _SUCCESSFUL_STATUS else False

    def retrieveData(self):
        """
        Retrieves the gff3 data for the associated job
        :return: gff3 content
        """
        _RETRIEVE_FUNCTION = 'retrieve_RAST_job'

        args = yaml.dump({'-format': 'gff3_stripped', '-job': self.jobId},
                         Dumper=yaml.RoundTripDumper)
        payload = {'function': _RETRIEVE_FUNCTION,
                   'username': self.username,
                   'password': self.password,
                   'args': args}

        retrieveReq = requests.post(RAST_URL, data=payload)
        retrieveReq.raise_for_status()

        return retrieveReq.text

    def deleteJob(self):
        """
        Deletes the current job
        """
        _DELETE_FUNCTION = 'delete_RAST_job'

        if self.jobId is None:
            raise RastException('RAST DELETE: No current job. Cannot delete.')

        payload = {'function': _DELETE_FUNCTION,
                   'username': self.username,
                   'password': self.password,
                   'args': '---\n-job:\n  - {}\n'.format(self.jobId)}

        deleteReq = requests.post(RAST_URL, data=payload)
        deleteReq.raise_for_status()

        deleteContent = yaml.safe_load(deleteReq.text)
        print(deleteContent[self.jobId]['status'])


if __name__ == '__main__':
    rast = Rast('mlazeroff', 'chester', 1)
    print(rast.checkIfComplete())
