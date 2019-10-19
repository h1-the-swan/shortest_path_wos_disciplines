# -*- coding: utf-8 -*-

DESCRIPTION = """utils for analyzing results"""

import sys, os, time, json
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

from collections import OrderedDict
import pandas as pd
import numpy as np

def load_samples_json(fname):
    with open(fname, 'r') as f:
        samples = json.load(f, object_pairs_hook=OrderedDict)
    return samples

def load_single_csv(fname):
    df_data = pd.read_csv(fname, header=None, names=['UID1', 'UID2', 'distance'])
    return df_data

def get_data_fnames(discipline_dir):
    data_fnames = glob(os.path.join(discipline_dir, '0*.csv'))
    data_fnames.sort()
    return data_fnames

def _get_dest_disciplines(samples, disc_idx_start, idx_start_within_disc_start):
    """
    :samples: OrderedDict with disciplines as keys and a 'UID' value containing a list of IDs
    :disc_idx_start: index of discipline to start with (e.g., 0 for Biology)
    :idx_start_within_disc_start: index of ID to start with within the discipline
    """
    disciplines = list(samples.keys())
    data = []
    for disc_idx, discipline in enumerate(disciplines[disc_idx_start:]):
        if disc_idx == disc_idx_start:
            ids = samples[discipline]['UID'][idx_start_within_disc_start:]
        else:
            ids = samples[discipline]['UID']
        for idx_within_disc, id_ in enumerate(ids):
            data.append( (id_, disc_idx, discipline, idx_within_disc) )
    return data

def yield_data_one_disc(discipline_dirs, samples):
    disc_data = _get_dest_disciplines(samples, 0, 0)
    df_disc = pd.DataFrame(disc_data, columns=['UID','disc_idx','disc','idx_within_disc'])
    for disc_idx in range(len(discipline_dirs)):
        discipline_dir = discipline_dirs[disc_idx]
        subset_disc = df_disc[df_disc['disc_idx']>=disc_idx]
        _dfs = []
        for idx_within_disc, fname in enumerate(get_data_fnames(discipline_dir)):
            _df = load_single_csv(fname)
            _df['disc_idx_1'] = disc_idx
            _df['disc_idx_2'] = subset_disc.iloc[idx_within_disc:]['disc_idx'].tolist()
            _dfs.append(_df)
        df_data = pd.concat(_dfs)
        yield df_data

def load_all_data(discipline_dirs, samples_json_fname):
    samples = load_samples_json(samples_json_fname)
    return pd.concat(x for x in yield_data_one_disc(discipline_dirs, samples))

# def main(args):
#     pass
#
# if __name__ == "__main__":
#     total_start = timer()
#     logger = logging.getLogger(__name__)
#     logger.info(" ".join(sys.argv))
#     logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
#     import argparse
#     parser = argparse.ArgumentParser(description=DESCRIPTION)
#     parser.add_argument("--debug", action='store_true', help="output debugging info")
#     global args
#     args = parser.parse_args()
#     if args.debug:
#         logger.setLevel(logging.DEBUG)
#         logger.debug('debug mode is on')
#     else:
#         logger.setLevel(logging.INFO)
#     main(args)
#     total_end = timer()
#     logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
