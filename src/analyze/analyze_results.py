# -*- coding: utf-8 -*-

DESCRIPTION = """Concatenate the results of the shortest path distance calculations, group by discipline, and aggregate"""

import sys, os, time
from glob import glob
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

from .analyze_util import load_all_data, load_samples_json
import pandas as pd
import numpy as np

def main(args):
    logger.debug("loading discipline dirs from base directory {}".format(args.datadir))
    discipline_dirs = glob(os.path.join(args.datadir, 'discipline*'))
    discipline_dirs.sort()
    logger.debug("loading data from {} discipline dirs...".format(len(discipline_dirs)))
    df_data = load_all_data(discipline_dirs, args.samples)
    # columns: [UID1, UID2, distance, disc_idx]

    if args.inf == 'drop':
        logger.debug("removing any rows with infinite distance")
        df_data = df_data[df_data.distance<10000]
    elif args.inf == 'max':
        # replace infinite values with the maximum distance in the data
        max_val = df_data.distance[df_data.distance<10000].max()
        logger.debug("replacing rows with infinite distance with distance: {}".format(max_val))
        df_data['distance'] = df_data['distance'].mask(df_data.distance>=10000, max_val)

    agg_funcs = [len, np.mean, np.std, np.median]
    logger.debug("calculating stats between disciplines...")
    df_stats = df_data.groupby(['disc_idx_1', 'disc_idx_2'])['distance'].agg(agg_funcs)
    logger.debug("writing to output file: {}".format(args.output))
    df_stats.to_csv(args.output)

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("datadir", help="base directory for data (should contain subdirectories, one for each discipline, named e.g., 'discipline001')")
    parser.add_argument("samples", help="path to samples data (JSON file)")
    parser.add_argument("output", help="path to output file (CSV)")
    parser.add_argument("--inf", default="drop", choices=('drop', 'max'), help="how to handle infinite distance values. Choices are 'drop' (drop these rows), or 'max' (set the value of these rows to the maximum distance found in the data)")
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
