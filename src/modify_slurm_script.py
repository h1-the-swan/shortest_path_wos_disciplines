# -*- coding: utf-8 -*-

DESCRIPTION = """Generate new Slurm scripts from template"""

import sys, os, time, re
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

from util import get_timestamp

def get_unique_log_filename(discipline_index, log_dir):
    """TODO: Docstring for get_unique_log_filename.

    :arg1: TODO
    :returns: TODO

    """
    i = 0
    # dt = get_timestamp('date')
    while True:
        # log_fname = os.path.join(log_dir, "calc_shortest_paths_discipline{:03d}_{:04d}_{}.log".format(discipline_index, i, dt))
        log_fname = os.path.join(log_dir, "calc_shortest_path_distances_discipline{:03d}_{:04d}.log".format(discipline_index, i))
        if not os.path.exists(log_fname):
            return log_fname
        i += 1

def main(args):
    fname = os.path.abspath(args.input)
    with open(fname, 'r') as f:
        txt = f.read()
    basedir = os.path.dirname(fname)
    for i in range(args.start, args.end+1):
        newtxt = re.sub(r"disc00", "disc{:02d}".format(i), txt)
        newtxt = re.sub(r"(data/processed.*?/)(discipline\d\d\d)", r"\1discipline{:03d}".format(i), newtxt)
        newtxt = re.sub(r"--discipline-index 0", "--discipline-index {}".format(i), newtxt)
        logfname = get_unique_log_filename(i, args.log_dir)
        # newtxt = re.sub(r"calc_shortest_path_distances_discipline000_", "calc_shortest_path_distances_discipline{:03d}_".format(i), newtxt)
        newtxt = re.sub(r"(>& )(.*?\.log)(\s)", r"\1{}\3".format(logfname), newtxt)
        outfname = "calc_shortest_paths_discipline{:03d}_slurm.sh".format(i)
        with open(os.path.join(basedir, outfname), 'w') as outf:
            outf.write(newtxt)
            

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("input", help="path to template slurm script")
    parser.add_argument("--start", type=int, default=0, help="start index")
    parser.add_argument("--end", type=int, default=36, help="end index (inclusive)")
    parser.add_argument("--log-dir", default='logs', help="path to directory with log files")
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
