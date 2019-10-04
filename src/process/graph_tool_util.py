# -*- coding: utf-8 -*-

DESCRIPTION = """processing utilities

`graph_tool` is a library that must be installed. Installing it is more complicated than simply using a package manager. Using a container (Singularity, or Docker) is a good way to use it.
"""

import sys, os, time, json
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

import graph_tool
from graph_tool.topology import shortest_distance
import pandas as pd
import numpy as np

def load_graph(tsv_fname, directed=True, skip_first=True, sep='\t'):
    """Load graph from a TSV edgelist file into graph-tool
    This will take a long time on large graphs (~2 hours for WoS 2018)

    :tsv_fname: path to edgelist file (TSV with header)
    :directed: if True, the graph has directed edges
    :skip_first: skip the first line of the TSV file (i.e., there is a header)
    :sep: delimiter for the TSV file (default: tab)
    :returns: graph_tool object

    """
    return graph_tool.load_graph_from_csv(tsv_fname, 
                                          directed=directed, 
                                          skip_first=skip_first, 
                                          csv_options={'delimiter': sep})

def get_name_to_vertices_dict(g):
    """Get a dictionary that maps vertices' names to the vertices objects

    :g: graph_tool graph

    """
    return {g.vp.name[v]: v for v in g.vertices()}

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
