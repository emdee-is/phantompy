#!/usr/local/bin/python3.sh
# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*

import sys
import os
import argparse

try:
    if 'COLOREDLOGS_LEVEL_STYLES' not in os.environ:
        os.environ['COLOREDLOGS_LEVEL_STYLES'] = 'spam=22;debug=28;verbose=34;notice=220;warning=202;success=118,bold;error=124;critical=background=red'
    # https://pypi.org/project/coloredlogs/
    import coloredlogs
except ImportError as e:
    coloredlogs = False

global LOG
import logging
import warnings
warnings.filterwarnings('ignore')
LOG = logging.getLogger()

def vsetup_logging(log_level, logfile='', stream=sys.stdout):
    global LOG
    add = True

    # stem fucks up logging
    from stem.util import log
    logging.getLogger('stem').setLevel(30)

    logging._defaultFormatter = logging.Formatter(datefmt='%m-%d %H:%M:%S')
    logging._defaultFormatter.default_time_format = '%m-%d %H:%M:%S'
    logging._defaultFormatter.default_msec_format = ''

    kwargs = dict(level=log_level,
                  force=True,
                  format='%(levelname)s %(message)s')

    if logfile:
        add = logfile.startswith('+')
        sub = logfile.startswith('-')
        if add or sub:
            logfile = logfile[1:]
        kwargs['filename'] = logfile

    if coloredlogs:
        # https://pypi.org/project/coloredlogs/
        aKw = dict(level=log_level,
                   logger=LOG,
                   stream=stream,
                   fmt='%(levelname)s %(message)s'
                   )
        coloredlogs.install(**aKw)
        if logfile:
            oHandler = logging.FileHandler(logfile)
            LOG.addHandler(oHandler)
        LOG.info(f"CSetting log_level to {log_level} {stream}")
    else:
        logging.basicConfig(**kwargs)
        if add and logfile:
            oHandler = logging.StreamHandler(stream)
            LOG.addHandler(oHandler)
        LOG.info(f"SSetting log_level to {log_level!s}")

        logging._levelToName = {
            logging.CRITICAL: 'CRITICAL',
            logging.ERROR: 'ERROR',
            logging.WARNING: 'WARN',
            logging.INFO: 'INFO',
            logging.DEBUG: 'DEBUG',
            logging.NOTSET: 'NOTSET',
        }
        logging._nameToLevel = {
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL,
            'ERROR': logging.ERROR,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET,
        }

def omain_argparser(_=None):

    try:
        from OpenSSL import SSL
        lCAfs = SSL._CERTIFICATE_FILE_LOCATIONS
    except:
        lCAfs = []

    CAfs = []
    for elt in lCAfs:
        if os.path.exists(elt):
            CAfs.append(elt)
    if not CAfs:
        CAfs = ['']

    parser = argparse.ArgumentParser(add_help=True,
                                     epilog=__doc__)
    parser.add_argument('--https_cafile', type=str,
                        help="Certificate Authority file (in PEM) (unused)",
                        default=CAfs[0])
    parser.add_argument('--log_level', type=int, default=20,
                        help="10=debug 20=info 30=warn 40=error")
    parser.add_argument('--js_input', type=str, default='',
                        help="Operate on the HTML file with javascript")
    parser.add_argument('--html_output', type=str, default='',
                        help="Write loaded and javascripted result to a HTML file")
    parser.add_argument('--pdf_output', type=str, default='',
                        help="Write loaded and javascripted result to a PDF file")
    parser.add_argument('--show_gui', type=bool, default=False, store_action=True,
                        help="show a progress meter that doesn't work")
    parser.add_argument('html_url', type=str, nargs='?',
                        required=True,
                        help='html file or url')
    return parser
