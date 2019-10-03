# -*- coding: utf-8 -*-

DESCRIPTION = """Convert samples data from CSV to JSON

Output will be in the format of a dictionary in which keys are disciplines ("Biology", ect.), 
and values are dictionaries of:
    "orig_index": list of integers,
    "UID": list of IDs (strings)
"""

import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

import pandas as pd
import numpy as np

def main(args):
    logger.debug("reading input file: {}".format(args.input))
    df = pd.read_csv(args.input, sep=',')
    logger.debug("input file has {} rows".format(len(df)))
    logger.debug("there are {} disciplines".format(df['discipline'].nunique()))

    logger.debug("grouping by 'discipline' and writing to file: {}".format(args.output))
    lists_by_discipline = df.groupby('discipline').agg(list)
    lists_by_discipline.to_json(args.output, orient='index')

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("input", help="path to input file (CSV)")
    parser.add_argument("output", help="path to output file (JSON)")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    else:
        logger.setLevel(logging.INFO)
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
