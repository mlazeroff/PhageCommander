import ast
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from phagecommander import Gene
import requests

URL = 'http://130.235.244.92/bcgi/aragorn.cgi'

TYPES = {'tRNA', 'tmRNA', 'both'}
SEQ_TOPOS = {'linear', 'circular'}
STRAND_TYPE = {'single', 'both'}


def aragorn_query(file_path: str, rna_type: str = 'tRNA', use_introns: bool = False, seq_topology: str = 'linear',
                  strand: str = 'both') -> List['Gene.TRNA']:
    """
    Calls Aragorn to analyze TRNA sequences in the DNA sequence
    :param file_path: fasta file path
    :param rna_type: {'tRNA', 'tmRNA', 'both'}
    :param use_introns:
    :param seq_topology: {'linear', 'circular'}
    :param strand: {'single', 'both'}
    :return: List[TRNA]
    """
    # check for valid parameters
    if rna_type not in TYPES:
        raise TypeError(f'{rna_type} is not a valid type {TYPES}')

    if use_introns:
        introns = 'yes'
    else:
        introns = 'no'

    if seq_topology not in SEQ_TOPOS:
        raise TypeError(f'{seq_topology} is not a valid sequence topology {SEQ_TOPOS}')

    file_path = Path(file_path)
    with open(file_path, 'r') as file:
        file_data = file.read()

    file_info = {'upload': (file_path.stem, file_data, 'application/octet-stream')}

    form_data = {
        'genome': 'NC_002695.fna',
        'search': rna_type,
        'intron': introns,
        'topology': seq_topology,
        'strand': strand,
        'output': 'tab-delimited',
        'submit': 'Submit'
    }

    file_post = requests.post(URL, data=form_data, files=file_info)
    file_post.raise_for_status()

    return file_post.content


def aragorn_parse(aragorn_data: str, id=None):
    soup = BeautifulSoup(aragorn_data, 'html.parser')
    trnas = soup.find('pre')

    genes: List['Gene.TRNA'] = []
    lines = trnas.text.split('\n')
    # total found on third line
    result_line = lines[2].split(' ')
    if int(result_line[0]) != 0:
        for line in lines[3:]:
            if 'tRNA' in line:
                line = line.split('\t')
                seq_data = line[0].split()
                rna = line[2]
                seq_type = seq_data[1] + rna
                # check if complement
                if seq_data[2][0] == 'c':
                    direction = '-'
                    start, stop = ast.literal_eval(seq_data[2][1:])
                else:
                    direction = '+'
                    start, stop = ast.literal_eval(seq_data[2])
                gene = Gene.TRNA(start, stop, direction, seq_type, identity=id)
                genes.append(gene)

    return genes
