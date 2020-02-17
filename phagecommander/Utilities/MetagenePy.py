import os
import requests
from bs4 import BeautifulSoup
from phagecommander import Gene

METAGENE_URL = 'http://metagene.nig.ac.jp/cgi-bin/mga.cgi'


class Metagene:

    def __init__(self, file: str, sequenceName: str = None):
        # check if file exists
        if not os.path.exists(file):
            raise FileExistsError('\"{}\" does not exist.'.format(file))

        self.file = file
        self.sequenceName = sequenceName

    def query(self):
        files = {'File': (self.sequenceName, open(self.file), 'application/octet-stream')}
        postReq = requests.post(METAGENE_URL, files=files)
        postReq.raise_for_status()
        return postReq.text

    @staticmethod
    def parse(metageneData: str, identity: str = ''):
        """
        Parse Metagene output data for Genes
        :param metageneData: metagene output file content
        :param identity: identity for each gene
        :return: List[Gene]
        """
        # indices
        START = 1
        STOP = 2
        DIRECTION = 3

        # parse html
        soup = BeautifulSoup(metageneData, 'html.parser')
        # find all genes
        geneLines = soup.find_all('tr')
        genes = []
        for line in geneLines:
            # split line content
            geneLine = line.find_all('td')
            start = geneLine[START].text
            stop = geneLine[STOP].text
            direction = geneLine[DIRECTION].text
            # create gene
            genes.append(Gene.Gene(start, stop, direction, identity=identity))

        return genes
