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
Install via pip and git
```angular2html
pip install git+https://github.com/mlazeroff/GeneQuery
```
## Using the tool

### GUI Version
Start via terminal
```angular2html
>>> genequery
```
OR

Start by double clicking the gene_query.pyw file
## Author
* **Matthew Lazeroff**
## License
This project is licensed under the GNU GPLv3
