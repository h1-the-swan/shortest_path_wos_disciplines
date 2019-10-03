# -*- coding: utf-8 -*-

DESCRIPTION = """Given the sample WoS IDs, remove all duplicates(??), and remove all IDs which do not appear in the citation network.

Uses Spark
"""

import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import pandas as pd
import numpy as np

from config import  Config

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

def get_vertices_from_edgelist(sdf_edges, src_colname='UID', dst_colname='cited_UID'):
    """Get all unique vertices from a two-column edgelist (Spark)

    :sdf_edges: spark dataframe
    :returns: spark dataframe

    """
    vertices_from_edgelist = sdf_edges.select([src_colname])
    vertices_from_edgelist = vertices_from_edgelist.union(sdf_edges.select([dst_colname]).withColumnRenamed(dst_colname, src_colname))
    vertices_from_edgelist = vertices_from_edgelist.drop_duplicates()
    return vertices_from_edgelist

def main(args):
    config = Config()
    spark = config.spark

    id_colname = 'UID'
    group_colname = 'discipline'

    df_samples = pd.read_csv(args.samples, index_col=0).drop_duplicates()
    logger.debug("{} rows read from file {}".format(len(df_samples), args.samples))
    logger.debug("there are {} unique IDs".format(df_samples[id_colname].nunique()))

    sdf_edges = spark.read.csv(args.edges, sep='\t', header=True)
    vertices_from_edgelist = get_vertices_from_edgelist(sdf_edges)
    
    sample_ids = df_samples[id_colname].unique().tolist()

    logger.debug("getting all IDs that are in the edgelist...")
    start = timer()
    result = vertices_from_edgelist.filter(vertices_from_edgelist.UID.isin(sample_ids)).toPandas()
    logger.debug("found {} IDs. This took {}".format(len(result), format_timespan(timer()-start)))

    # align sample IDs with this result
    df_samples = df_samples[df_samples[id_colname].isin(result[id_colname])]
    df_samples.index.name = 'orig_index'
    df_samples = df_samples.reset_index(drop=False)

    logger.debug("writing {} rows to {}".format(len(df_samples), args.output))
    df_samples.to_csv(args.output, index=False)

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("samples", help="path to CSV file with WoS samples. columns 'UID', 'discipline'")
    parser.add_argument("edges", help="path to file or directory with the full WoS citation edgelist (TSV format, with header)")
    parser.add_argument("output", help="path to output file (CSV)")
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
