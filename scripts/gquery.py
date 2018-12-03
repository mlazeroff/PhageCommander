from genequery import Gene
import argparse
import os


def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('sequence', help='DNA sequence file')
    parser.add_argument('species', help='DNA species, see species.txt for full list')
    parser.add_argument('output', help='Output directory')
    parser.add_argument('-rm', help='Remove all Glimmer/GeneMark output files', action='store_true')
    args = parser.parse_args()

    # create sequence
    sequence = Gene.GeneFile(args.sequence, args.species)

    # check if output directory exists, if not, create it
    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    # query
    files = sequence.query_all(output=args.output)

    # write to Excel file
    Gene.excel_write(args.output, files, sequence)

    # If -rm flag given, remove all output files
    if args.rm:
        for file in files:
            os.remove(file)


if __name__ == '__main__':
    main()