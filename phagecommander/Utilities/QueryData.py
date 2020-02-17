import json

from phagecommander import Gene


class QueryData:
    """
    Class for representing tool/species selections
    """

    def __init__(self):
        # tools to call
        self.tools = {key: True for key in Gene.TOOLS}
        # species of the DNA sequence
        self.species = ''
        # path of the DNA file
        self.fileName = ''
        # tool data
        # Key - tool (from TOOL_NAMES)
        # Value - List of Genes
        self.toolData = dict()
        # sequence
        self.sequence = ''
        # RAST related information
        self.rastUser = ''
        self.rastPass = ''
        self.rastJobID = None
