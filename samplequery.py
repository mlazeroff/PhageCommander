"""
GeneMark Query
Author: Matthew Lazeroff
"""

import requests
from bs4 import BeautifulSoup

# Genemark Domains
FILE_DOMAIN = 'http://exon.biology.gatech.edu/GeneMark/'
GM_DOMAIN = 'http://exon.gatech.edu/GeneMark/gm.cgi'
GM_HMM_DOMAIN = 'http://exon.gatech.edu/GeneMark/gmhmmp.cgi'
GMS_DOMAIN = 'http://exon.gatech.edu/GeneMark/genemarks.cgi'
HEURISTIC_DOMAIN = 'http://exon.gatech.edu/GeneMark/heuristic_gmhmmp.cgi'
GMS2_DOMAIN = 'http://exon.gatech.edu/GeneMark/genemarks2.cgi'


class Error(Exception):
    """
    Base Error Class
    """
    pass


class GeneMarkError(Error):
    """
    Raised when no result from GeneMark is returned
    """

    def __init__(self, message):
        self.message = message


class GeneFile:
    def __init__(self, sequence_file):
        """
        Constructor
        Generates necessary parameters for post requests from DNA fasta file
        :param sequence_file:
        """
        # Load DNA Sequence into memory
        input_file_data = b''
        with open(sequence_file, 'rb') as input_file:
            current_byte = input_file.read(1)
            while (current_byte):
                input_file_data += current_byte
                current_byte = input_file.read(1)

        self.name = 'Diane complete'

        # File creation for post requests
        self.file_info = {'file': (self.name, input_file_data, 'application/octet-stream')}

    def genemark_query(self):
        """
        Query to GeneMark
        :return:
        """
        # Begin GeneMark Lookup -----------------------------------------------------
        gm_data = {'sequence': '', 'org': 'Escherichia_coli_K_12_substr__MG1655',
                   'submit': 'Start GeneMark', 'email': '', 'subject': 'GeneMark', 'windowsize': 96,
                   'stepsize': 12, 'threshold': 0.5, 'rbs': 'none', 'mode': 'native'}

        # GeneMark post - if unsuccessful, error thrown
        gm_post_request = requests.post(GM_DOMAIN, files=self.file_info, data=gm_data)
        gm_post_request.raise_for_status()
        soup = BeautifulSoup(gm_post_request.text, 'html.parser')

        # Get URL for gm output
        file_location = ''
        for a in soup.find_all('a', href=True):
            if 'tmp' in a['href']:
                file_location = a['href']
                break

        # if tmp not available, change in response format or invalid post
        try:
            if file_location == '':
                raise GeneMarkError("GeneMark")
        except GeneMarkError:
            raise

        # write gm response to file
        gm_output = open(self.name + '.gm', 'wb')
        getGMFile = requests.get(FILE_DOMAIN + file_location)
        getGMFile.raise_for_status()
        gm_output.write(getGMFile.content)
        # End GeneMark Lookup -------------------------------------------------------

    def genemarkhmm_query(self):
        # Begin GeneMark Hmm Lookup -------------------------------------------------
        gm_hmm_data = {'sequence': '', 'org': 'Escherichia_coli_K_12_substr__MG1655',
                       'submit': 'Start GeneMark.hmm', 'format': 'LST',
                       'subject': 'GeneMark.hmm prokaryotic',
                       'email': ''}

        # GeneMark hmm post - if unsuccessful, error thrown
        hmm_post_request = requests.post(GM_HMM_DOMAIN, files=self.file_info, data=gm_hmm_data)
        hmm_post_request.raise_for_status()
        soup = BeautifulSoup(hmm_post_request.text, 'html.parser')

        # Get URL for hmm output
        file_location = ''
        for a in soup.find_all('a', href=True):
            if 'tmp' in a['href']:
                file_location = a['href']
                break

        # if tmp not available, change in response format or invalid post
        try:
            if file_location == '':
                raise GeneMarkError("GeneMark Hmm")
        except GeneMarkError:
            raise

        # write response to file
        gmhmm_output = open(self.name + '.gmhmm', 'wb')
        getHmmFile = requests.get(FILE_DOMAIN + file_location)
        getHmmFile.raise_for_status()
        gmhmm_output.write(getHmmFile.content)
        # End GeneMark Hmm Lookup --------------------------------------------------

    def genemarks_query(self):
        # Begin GeneMarkS Lookup ---------------------------------------------------
        gms_data = {'sequence': '', 'submit': 'Start GeneMarkS', 'mode': 'prok', 'format': 'LST',
                    'subject': 'GeneMarkS', 'gcode': 11}

        # GeneMarkS post - if unsuccessful, error thrown
        gms_post_request = requests.post(GMS_DOMAIN, files=self.file_info, data=gms_data)
        gms_post_request.raise_for_status()
        soup = BeautifulSoup(gms_post_request.text, 'html.parser')

        # Get URL for hmm output
        file_location = ''
        for a in soup.find_all('a', href=True):
            if 'tmp' in a['href']:
                file_location = a['href']
                break

        # if tmp not available, change in response format or invalid post
        try:
            if file_location == '':
                raise GeneMarkError("GeneMarkS")
        except GeneMarkError:
            raise

        # write response to file
        gms_output = open(self.name + '.gms', 'wb')
        getGmsFile = requests.get(FILE_DOMAIN + file_location)
        getGmsFile.raise_for_status()
        gms_output.write(getGmsFile.content)
        # End GeneMarkS Lookup -----------------------------------------------------

    def genemark_heuristic_query(self):
        """
        Query GeneMark Heuristic
        """
        # Begin GeneMark Heuristic Lookup ------------------------------------------
        heuristic_data = {'sequence': '', 'submit': 'Start GeneMark.hmm', 'format': 'LST',
                          'email': '',
                          'subject': 'GeneMark.hmm', 'gcode': 11, 'strand': 'both',
                          'mod_type': 1999}

        # GeneMark Heuristic post - if unsuccessful, error thrown
        heuristic_post_request = requests.post(HEURISTIC_DOMAIN, files=self.file_info,
                                               data=heuristic_data)
        heuristic_post_request.raise_for_status()
        soup = BeautifulSoup(heuristic_post_request.text, 'html.parser')

        # Get URL for heuristic output
        file_location = ''
        for a in soup.find_all('a', href=True):
            if 'tmp' in a['href']:
                file_location = a['href']
                break

        # if tmp not available, change in response format or invalid post
        try:
            if file_location == '':
                raise GeneMarkError("GeneMark Heuristic")
        except GeneMarkError:
            raise

        # write response to file
        heuristic_output = open(self.name + '.heuristic', 'wb')
        getHeuristicFile = requests.get(FILE_DOMAIN + file_location)
        getHeuristicFile.raise_for_status()
        heuristic_output.write(getHeuristicFile.content)
        # End GeneMark Heuristic Lookup -------------------------------------------

    def genemarks2_query(self):
        """
        Query GeneMarkS2
        """
        # Begin GeneMarkS2 Lookup -------------------------------------------------
        gmms2_data = {'sequence': '', 'submit': 'GeneMarkS-2', 'mode': 'auto', 'format': 'lst',
                      'email': '', 'subject': 'GeneMarkS-2', 'gcode': 11}

        # GeneMarkS2 Post Request
        gmms2_post_request = requests.post(GMS2_DOMAIN, files=self.file_info, data=gmms2_data)
        gmms2_post_request.raise_for_status()
        soup = BeautifulSoup(gmms2_post_request.text, 'html.parser')

        # Get URL for GMS2 output
        file_location = ''
        for a in soup.find_all('a', href=True):
            if 'tmp' in a['href']:
                file_location = a['href']
                break

        # if tmp not available, change in response format or invalid post
        try:
            if file_location == '':
                raise GeneMarkError("GeneMarkS2")
        except GeneMarkError:
            raise

        # write response to file
        gms2_output = open(self.name + '.gms2', 'wb')
        getGMS2File = requests.get(FILE_DOMAIN + file_location)
        getGMS2File.raise_for_status()
        gms2_output.write(getGMS2File.content)
        # End GeneMarkS2 Lookup --------------------------------------------------

    def query_all(self):
        """
        Query: GeneMark, GeneMarkHmm, GeneMarkS, GeneMarkS2, and GeneMark Heuristic
        """
        self.genemark_query()
        self.genemarkhmm_query()
        self.genemarks_query()
        self.genemarks2_query()
        self.genemark_heuristic_query()




if __name__ == '__main__':
    file = 'D:\mdlaz\Documents\college\Research\PhageProject_Sept2018\GeneSequences\Diane complete.fasta'

    # Create GeneFile from sequence file and query
    sequence = GeneFile(file)
    sequence.query_all()
