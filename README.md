# GeneQuery
Tool for compiling GeneMark/Glimmer data for a Fasta DNA sequence
## Overview
GeneQuery takes a Fasta DNA sequence file, calls GeneMark/Glimmer gene-encoding prediction tools, and generates an Excel spreadsheet of all gene predictions. The Excel document is organized by color, with darker colors representing a greater number of tools predicting the same genes and lighter colors representing fewer tools.

The following gene-encoding prediction tools are called:
* Glimmer
* Genemark
* Genemark Hmm
* GenemarkS
* GenemarkS2
* Genemark Heuristic
## Getting Started
### Prerequisites
* Python 3.*
* Windows (note - may work with other operating systems, but not guaranteed)
### Installing
Download the repository
```angular2html
git clone https://github.com/mlazeroff/GeneQuery
```
Install with pip
```angular2html
pip install ./GeneQuery
```
## Using the tool
### Terminal Version
Usage: python3 Gene "fasta_sequence" "species" "output_directory" -rm
* fasta_sequence - Fasta formatted DNA sequence file
* species - DNA species, full list located in species.txt
* output_directory  - folder to output files to
* -rm - delete intermediate output files, leaves only .xlsx file
```angular2html
>>> python3 Gene Lisa.fasta Acidianus_hospitalis_W1 ./output/
Querying:
Glimmer...done
GeneMark...done
Hmm...done
GMS...done
GMS2...done
Heuristic...done
Files written to: ./output/
>>>
```
### GUI Version
Start via terminal
```angular2html
python3 GeneQuery
```
OR

Start by double clicking the GeneQuery.pyw file
## Author
* **Matthew Lazeroff**
## License
This project is licensed under the GNU GPLv3
