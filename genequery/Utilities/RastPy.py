import os
import requests
import yaml

RAST_URL = 'http://pubseed.theseed.org/rast/server.cgi'


class Rast:
    """
    Class for representing queries to RAST annotation servers
    """
    class RastException(Exception):
        pass

    def __init__(self, username: str, password: str):
        """
        :param username:
        :param password:
        """
        self.username = username
        self.password = password
        self.file = None
        self.jobId = None
        self.status = None

    def submit(self, filePath: str, sequenceName: str):
        """
        Submits a file for annotation
        :param filePath: name of a fasta file
        :param sequenceName: name of the sequence
        Raises an exception if not successful
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
                          '-taxonomyID': '',
                          '-file': fastaContent}, default_style='|')

        payload = {'function': _SUBMIT_FUNCTION,
                   'args': args,
                   'username': self.username,
                   'password': self.password}

        submitReq = requests.post(RAST_URL, data=payload)

        submitResponse = yaml.load(submitReq.text, Loader=yaml.FullLoader)
        if submitResponse['status'] == 'ok':
            self.jobId = submitResponse['job_id']
            self.status = 'incomplete'
        else:
            raise self.RastException('Received status response of :{}'.format(submitResponse['status']))


