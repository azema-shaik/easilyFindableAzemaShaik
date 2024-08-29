import argparse

parser = argparse.ArgumentParser( description = "Run agent as command line utility")
parser.add_argument( "query", metavar = 'QUERY', type = str, 
                    help = "user query for the system")
parser.add_argument('-o','--output-file', help = "output will be written to this file",type = str)
args = parser.parse_args()

from info_bot import main
main(args.query, args.output_file)