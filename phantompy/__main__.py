#!/usr/local/bin/python3.sh
# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*

from __future__ import absolute_import
import sys

from .qasync_phantompy import iMain

try:
    from .support_phantompy import vsetup_logging
    d = int(os.environ.get('DEBUG', 0))
    if d > 0:
        vsetup_logging(10, stream=sys.stderr)
    else:
        vsetup_logging(20, stream=sys.stderr)
    vsetup_logging(log_level, logfile='', stream=sys.stderr)
except: pass

if __name__ == '__main__':
    iMain(sys.argv[1:])
