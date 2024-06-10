import sys
import optparse
import collections

import pressagio.tokenizer
import pressagio.dbconnector

###################################### Main


def main():
    # parse command line options
    usage = "usage: %prog [options] file1 file2 ..."
    parser = optparse.OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option(
        "-n", "--ngram", dest="ngram", type="int", help="Specify ngram cardinality N"
    )
    parser.add_option(
        "-l",
        "--lowercase",
        dest="lowercase",
        default=False,
        help="Enable lowercase conversion mode",
    )
    parser.add_option(
        "-a",
        "--append",
        dest="append",
        default=False,
        help="Enable append mode for database",
    )
    parser.add_option("-o", "--output", dest="outfile", help="Output file name O")
    (options, infiles) = parser.parse_args()

    if not infiles:
        parser.error("Please provide input files.")

    if not options.ngram:
        parser.error("Please specify n-gram cardinality.")

    if not options.outfile:
        parser.error("Please specify output file.")

    # now parse all files
    for infile in infiles:
        print("Parsing {0}...".format(infile))
        ngram_map = pressagio.tokenizer.forward_tokenize_file(
            infile, options.ngram, options.lowercase
        )

    # write to sqlite database
    print("Writing result to {0}...".format(options.outfile))
    pressagio.dbconnector.insert_ngram_map_sqlite(
        ngram_map, options.ngram, options.outfile, options.append
    )


###################################### Helpers


if __name__ == "__main__":
    main()