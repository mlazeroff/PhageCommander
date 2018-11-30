"""
GeneMark Query
Author: Matthew Lazeroff
"""

import requests
import threading
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
    """
    Class for querying GeneMark tools for a DNA sequence
    """

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

    def genemark_query(self, out=''):
        """
        Query to GeneMark
        :param out: optional output file name
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
        if out != '':
            gm_output = open(out, 'wb')
        else:
            gm_output = open(self.name + '.gm', 'wb')
        getGMFile = requests.get(FILE_DOMAIN + file_location)
        getGMFile.raise_for_status()
        gm_output.write(getGMFile.content)
        # End GeneMark Lookup -------------------------------------------------------

    def genemarkhmm_query(self, out=''):
        """
        Query GeneMark Hmm
        :param out: optional output file name
        :return:
        """
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
        if out != '':
            gmhmm_output = open(out, 'wb')
        else:
            gmhmm_output = open(self.name + '.gmhmm', 'wb')
        getHmmFile = requests.get(FILE_DOMAIN + file_location)
        getHmmFile.raise_for_status()
        gmhmm_output.write(getHmmFile.content)
        # End GeneMark Hmm Lookup --------------------------------------------------

    def genemarks_query(self, out=''):
        """
        Query GeneMarkS
        :param out: optional output file name
        """
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
        if out != '':
            gms_output = open(out, 'wb')
        else:
            gms_output = open(self.name + '.gms', 'wb')
        getGmsFile = requests.get(FILE_DOMAIN + file_location)
        getGmsFile.raise_for_status()
        gms_output.write(getGmsFile.content)
        # End GeneMarkS Lookup -----------------------------------------------------

    def genemark_heuristic_query(self, out=''):
        """
        Query GeneMark Heuristic
        :param out: optional output file name
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
        if out != '':
            heuristic_output = open(out, 'wb')
        else:
            heuristic_output = open(self.name + '.heuristic', 'wb')
        getHeuristicFile = requests.get(FILE_DOMAIN + file_location)
        getHeuristicFile.raise_for_status()
        heuristic_output.write(getHeuristicFile.content)
        # End GeneMark Heuristic Lookup -------------------------------------------

    def genemarks2_query(self, out=''):
        """
        Query GeneMarkS2
        :param out: optional output file name
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
        if out != '':
            gms2_output = open(out, 'wb')
        else:
            gms2_output = open(self.name + '.gms2', 'wb')
        getGMS2File = requests.get(FILE_DOMAIN + file_location)
        getGMS2File.raise_for_status()
        gms2_output.write(getGMS2File.content)
        # End GeneMarkS2 Lookup --------------------------------------------------

    def query_all(self):
        """
        Query: GeneMark, GeneMarkHmm, GeneMarkS, GeneMarkS2, and GeneMark Heuristic
        """
        # Methods to query
        queries = [self.genemark_query, self.genemarkhmm_query, self.genemarks_query,
                   self.genemarks2_query,
                   self.genemark_heuristic_query]

        # Thread pool
        threads = []

        # Allocate threads
        for query in queries:
            threads.append(threading.Thread(target=query))

        # Start Threads
        for thread in threads:
            thread.start()

        # Join Threads
        for thread in threads:
            thread.join()


class GeneError(Error):
    def __init__(self, message):
        self.message = message


class Gene:
    """
    Class for representing a potential gene encoding
    """

    def __init__(self, start, stop, direction, length):
        """
        Constructor
        :param start:  start codon (int)
        :param stop:   end codon (int)
        :param direction: +/-
        :param length: length of gene (int)
        """
        self.start = int(start)
        self.stop = int(stop)
        # check for proper direction
        try:
            if direction != '+' and direction != '-':
                raise GeneError("Direction must be + or -")
            else:
                self.direction = direction
        except GeneError:
            raise
        self.length = int(length)

    def __str__(self):
        """
        Overload of str() for printing
        :return: String containing gene information
        """
        return 'Direction: {} Start: {} Stop: {} Length: {}'.format(self.direction,
                                                                    self.start,
                                                                    self.stop,
                                                                    self.length)


class GeneParse:
    """
    Class for parsing GeneMark output files
    All methods are static
    """

    @staticmethod
    def parse_genemark(gm_file):
        file = open(gm_file, 'r')

        # Skip until Regions of Interests
        curr_line = file.readline()
        while (' LEnd      REnd    Strand      Frame' not in curr_line):
            curr_line = file.readline()

        # read blank line
        curr_line = file.readlines(2)

        # Get gene data
        curr_line = file.readline()
        genes = []
        while curr_line != '\n':
            data = [x for x in curr_line.strip().split(' ') if x != '']
            # check gene orientation
            if data[2] == 'direct':
                direction = '+'
            else:
                direction = '-'
            # get gene length
            length = int(data[1]) - int(data[0]) + 1
            # add to list
            genes.append(Gene(data[0], data[1], direction, length))
            curr_line = file.readline()

        return genes

    @staticmethod
    def parse_genemarkS(s_file):
        """
        Parse GeneMarkS file for Gene data
        :param s_file: GeneMarkS file
        :return: list of Gene objects in file order
        """
        file = open(s_file, 'r')

        # begin parse
        current_line = file.readline()
        # Check if proper GeneMark file
        try:
            if 'GeneMark.hmm' not in current_line:
                raise GeneError("Hmm: Not a valid GeneMark Hmm file")
        except GeneError:
            raise

        # skip through until gene data
        while ('Gene    Strand    LeftEnd    RightEnd       Gene     Class' not in current_line):
            current_line = file.readline()
        current_line = file.readline()  # read blank line

        # arary for gene objs
        genes = []
        # get gene data
        current_line = file.readline()
        while current_line != '\n':
            data = [x for x in current_line.strip().split(' ') if x != '']
            genes.append(Gene(data[2], data[3], data[1], data[4]))
            current_line = file.readline()

        return genes

    @staticmethod
    def parse_genemarkHmm(hmm_file):
        """
        Parse GeneMark Hmm file for Gene data
        :param hmm_file:
        :return: list of Gene objects in file order
        """
        file = open(hmm_file, 'r')

        # begin parse
        current_line = file.readline()
        # Check if proper GeneMark file
        try:
            if 'GeneMark.hmm' not in current_line:
                raise GeneError("Hmm: Not a valid GeneMark Hmm file")
        except GeneError:
            raise

        # skip through until gene data
        while ('Gene    Strand    LeftEnd    RightEnd       Gene     Class' not in current_line):
            current_line = file.readline()
        current_line = file.readline()  # read blank line

        # arary for gene objs
        genes = []
        # get gene data
        current_line = file.readline()
        while current_line != '\n':
            data = [x for x in current_line.strip().split(' ') if x != '']
            genes.append(Gene(data[2], data[3], data[1], data[4]))
            current_line = file.readline()

        return genes

    @staticmethod
    def parse_genemarkHeuristic(heuristic_file):
        """
        Parse GeneMark Heuristic file for Gene data
        :param heuristic_file: GeneMark Heuristic output file
        :return: list of Gene objects in order
        """
        file = open(heuristic_file, 'r')

        # begin parse
        current_line = file.readline()
        # Check if proper GeneMark file
        try:
            if 'GeneMark.hmm' not in current_line:
                raise GeneError("Hmm: Not a valid GeneMark Hmm file")
        except GeneError:
            raise

        # skip through until gene data
        while ('Gene    Strand    LeftEnd    RightEnd       Gene     Class' not in current_line):
            current_line = file.readline()
        current_line = file.readline()  # read blank line

        # arary for gene objs
        genes = []
        # get gene data
        current_line = file.readline()
        while current_line != '\n':
            data = [x for x in current_line.strip().split(' ') if x != '']
            genes.append(Gene(data[2], data[3], data[1], data[4]))
            current_line = file.readline()

        return genes

    @staticmethod
    def parse_genemarkS2(s2_file):
        """
        Parse GeneMark S2 file for Gene data
        :param s2_file: GeneMark S2 output file
        :return: list of Gene objects in file order
        """
        file = open(s2_file, 'r')

        # skip until gene data
        curr_line = file.readline()
        while ('SequenceID' not in curr_line):
            curr_line = file.readline()

        # Get gene data
        genes = []
        curr_line = file.readline()
        while curr_line != '\n':
            data = [x for x in curr_line.strip().split(' ') if x != '']
            genes.append(Gene(data[2], data[3], data[1], data[4]))
            curr_line = file.readline()

        return genes


if __name__ == '__main__':
    my_file = 'D:\mdlaz\Documents\college\Research\PhageProject_Sept2018\GeneSequences\Diane complete.fasta'
    # Create GeneFile from sequence file and query
    sequence = GeneFile(my_file)
    for x in GeneParse.parse_genemark('Diane complete.gm'):
        print(x)
