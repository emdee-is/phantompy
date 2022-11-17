# -*- mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*-

# (c) 2018 Gerard Marull-Paretas <gerard@teslabs.com>
# (c) 2014 Mark Harviston <mark.harviston@gmail.com>
# (c) 2014 Arve Knudsen <arve.knudsen@gmail.com>
# BSD License

# phantompy test - just test qasync for now

import os
import logging
from pytest import fixture

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

@fixture(scope="session")
def application():
    from phantompy.qasync_phantompy import QApplication

    return QApplication([])
