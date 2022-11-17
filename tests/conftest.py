# © 2018 Gerard Marull-Paretas <gerard@teslabs.com>
# © 2014 Mark Harviston <mark.harviston@gmail.com>
# © 2014 Arve Knudsen <arve.knudsen@gmail.com>
# BSD License

# phantompy test - just test qasync for now

import os
import logging
from pytest import fixture


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


if os.name == "nt":
    collect_ignore = ["qasync/_unix.py"]
else:
    collect_ignore = ["qasync/_windows.py"]


@fixture(scope="session")
def application():
    from phantompy.qasync_phantompy import QApplication

    return QApplication([])
