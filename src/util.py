# -*- coding: utf-8 -*-

DESCRIPTION = """general project utilities"""

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

def get_unique_filename(basename='calc_times', ext='.csv', start_num=0, basedir='.'):
    """Get a filename, incrementing number until it finds a file path that doesn't exist
    e.g., if `calc_times_000.csv` already exists, return `calc_times_001.csv`

    :returns: filename

    """
    basename = basename.strip('_')
    ext = ext.strip('.')
    i = start_num
    while True:
        fname = os.path.join(basedir, '{}_{:03}.{}'.format(basename, i, ext))
        if not os.path.exists(fname):
            return fname
        i += 1

def get_timestamp(res='seconds', dt=None):
    """Get current timestamp as a string of integers

    :res: resolution. one of:
        'seconds' (default): date + time to the second, e.g., 201910040945,
        'micro' or 'ms': date + time to the millisecond
        'minute' or 'min': date + time to the minute, e.g., 2019100409,
        'date': date, e.g., 20191004,
        'month' or 'mo': date to the month, e.g., 201910
    :dt: The default is to use the current date and time. If `dt` is specified (as a datetime object), use that instead.

    """
    fmt = "%Y%m"
    res = res.lower()
    if dt is None:
        dt = datetime.now()
    if res.startswith('mo'):
        return datetime.strftime(dt, fmt)
    fmt += "%d"
    if res == 'date':
        return datetime.strftime(dt, fmt)
    fmt += "%H%M"
    if res.startswith('min'):
        return datetime.strftime(dt, fmt)
    fmt += "%S"
    if res.startswith('sec'):
        return datetime.strftime(dt, fmt)
    fmt += "%f"
    if res.startswith('micro') or res.startswith('ms'):
        return datetime.strftime(dt, fmt)
    raise ValueError("Invalid value specified for 'res'")



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
