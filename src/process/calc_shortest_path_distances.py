# -*- coding: utf-8 -*-

DESCRIPTION = """TODO: description"""

import sys, os, time, json, warnings
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
from ..util import get_unique_filename

try:
    from .graph_tool_util import load_graph, get_name_to_vertices_dict
    from graph_tool.topology import shortest_distance
except ImportError:
    warnings.warn("It seems that graph-tool is not installed in this environment. Some things may not work.")
    

def build_sample_set(samples, discipline_index):
    """collect the IDs to calculate distance on

    :samples: dictionary loaded from input JSON file
    :discipline_index: index of the discipline within the OrderedDict of the `samples` file (i.e., '0' would mean the first discipline)
    :returns: sample_ids: list of all IDs to be used as target IDs
              source_ids: list of all IDs to be used as source IDs (potentially with a lot of overlap with the target IDs)
              discipline_name: name of the discipline

    """
    sample_ids = []
    source_ids = []
    ignore_mode = True
    for i, k in enumerate(samples):
        if i == discipline_index:
            discipline_name = k
            ignore_mode = False
            source_ids = samples[k]['UID']

        if ignore_mode is True:
            continue
        else:
            _ids = samples[k]['UID']
            sample_ids.extend(_ids)
    return sample_ids, source_ids, discipline_name


def main(args):
    outdir = os.path.abspath(args.outdir)
    if not os.path.exists(outdir):
        logger.debug("creating output directory: {}".format(outdir))
        os.mkdir(outdir)
    else:
        logger.debug("using output directory: {}".format(outdir))

    logger.debug("loading file with sample IDs: {}".format(args.sample_ids))
    with open(args.sample_ids, 'r') as f:
        samples = json.load(f, object_pairs_hook=OrderedDict)
    sample_ids, source_ids, discipline_name = build_sample_set(samples, args.discipline_index)
    logger.debug("using discipline {} (index {})".format(discipline_name, args.discipline_index))

    fname_calc_times = get_unique_filename(basename='calc_times', ext='.csv', basedir=outdir)
    f_calc_times = open(fname_calc_times, 'w', buffering=1)
    sep = ','
    logger.debug("writing header to {}".format(fname_calc_times))
    f_calc_times.write("source_name{sep}calc_time{sep}distance_fname\n".format(sep=sep))

    
    start = timer()
    logger.debug("loading graph from {}. This will take a while...".format(args.edges))
    g = load_graph(args.edges)
    logger.debug("done loading graph. Took {}".format(format_timespan(timer()-start)))

    start = timer()
    logger.debug("creating dictionary of name to vertices...")
    name_to_v = get_name_to_vertices_dict(g)
    logger.debug("done loading dictionary. Took {}".format(format_timespan(timer()-start)))

    start = timer()
    logger.debug("starting shortest path calculations...")
    if args.undirected is True:
        logger.debug("treating graph as undirected for shortest distance calculations")
        directed = False
    else:
        directed = None

    vertices_sample = [name_to_v[wos_id] for wos_id in sample_ids]
    vertices_source = [name_to_v[wos_id] for wos_id in source_ids]
    logger.debug("number of sample vertices: {}".format(len(vertices_sample)))

    for i, source in enumerate(vertices_source):
        this_start = timer()
        source_name = g.vp.name[source]
        outfname = "{:012d}.csv".format(i)  
        outfname = os.path.join(outdir, outfname)
        if os.path.exists(outfname):
            logger.debug("filename {} already exists. skipping.".format(outfname))
        else:
            logger.debug("calculating shortest distance for vertex: name: {}".format(source_name))
            dist = shortest_distance(g, source=source, target=vertices_sample, directed=directed)
            this_time = timer() - this_start
            with open(outfname, 'w') as outf:
                for i_dist, x in enumerate(dist):
                    # outf.write("{}\n".format(x))
                    outf.write("{source_name}{sep}{target_name}{sep}{distance}\n".format(sep=sep, source_name=source_name, target_name=sample_ids[i_dist], distance=x))
            f_calc_times.write("{source_name}{sep}{calc_time}{sep}{distance_fname}\n".format(sep=sep, source_name=source_name, calc_time=this_time, distance_fname=os.path.basename(outfname)))
        vertices_sample = vertices_sample[1:]  # vertices to process will shrink by one each time through the loop. FIFO.
        sample_ids = sample_ids[1:]

    logger.debug("finished shortest path calculations. Took {}".format(format_timespan(timer()-start)))
    f_calc_times.close()

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("edges", help="path to edges TSV (with header)")
    parser.add_argument("sample_ids", help="path to file with sample IDs. JSON file")
    parser.add_argument("outdir", help="path to output directory")
    parser.add_argument("-d", "--discipline-index", type=int, default=0, help="index of the discipline whose sample IDs to use as source")
    # parser.add_argument("-i", "--start-index", type=int, default=0, help="within the discipline, index of the sample ID to start with")
    parser.add_argument("--id-colname", default='UID', help="column name for ID in the `sample_ids` file (default: 'UID')")
    parser.add_argument("--undirected", action='store_true', help="treat graph as undirected for shortest distance calculations")
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
