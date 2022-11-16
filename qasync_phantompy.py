#!/usr/local/bin/python3.sh
# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*

import sys
import os
import qasync
import asyncio
import time
import random

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QProgressBar, QWidget, QVBoxLayout)

from phantompy import Render
# from lookupdns import LookFor as Render

global LOG
import logging
import warnings
warnings.filterwarnings('ignore')
LOG = logging.getLogger()

class Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self._label = QtWidgets.QLabel()
        box = QtWidgets.QHBoxLayout()
        self.setLayout(box)
        box.addWidget(self._label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 99)
        box.addWidget(self.progress)

    def update(self, text):
        i = len(asyncio.all_tasks())
        self._label.setText(str(i))
        self.progress.setValue(int(text))
        
class ContextManager:
    def __init__(self) -> None:
        self._seconds = 0
    async def __aenter__(self):
        LOG.debug("ContextManager enter")
        return self
    async def __aexit__(self, *args):
        LOG.debug("ContextManager exit")
    async def tick(self):
        await asyncio.sleep(1)
        self._seconds += 1
        return self._seconds

async def main(widget, app, ilen):
    LOG.debug("Task started")
    try:
        async with ContextManager() as ctx:
            for i in range(1, 120):
                seconds = await ctx.tick()
                if widget:
                    widget.update(str(i))
                if len(app.ldone) == ilen:
                    LOG.info(f"Finished with {app.ldone}")
                    print('\n'.join(app.ldone))
                    app.exit()
                    # raise  asyncio.CancelledError
                    return
                LOG.debug(f"{app.ldone} {perc} {seconds}")
    except asyncio.CancelledError as ex:
        LOG.debug("Task cancelled")

def iMain(largs, bgui=True):
    app = QtWidgets.QApplication([])
    app.lstart = []
    if bgui:
        widget = Widget()
        widget._app = app
        widget.show()
    else:
        widget = None
        
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    largs = sys.argv[1:]
    url = largs[0]
    outfile = largs[1]
    jsfile = largs[2] if len(largs) > 2 else None
    # run only starts the url loading
    r = Render(app, do_print=False, do_save=True)
    uri = url.strip()
    r.run(uri, outfile, jsfile)
    LOG.debug(f"{r.percent} {app.lstart}")
    
    LOG.info(f"queued {len(app.lstart)} urls")
        
    task = loop.create_task(main(widget, app, 1))
    loop.run_forever()

    # cancel remaining tasks and wait for them to complete
    task.cancel()
    tasks = asyncio.all_tasks()
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    try:
        from exclude_badExits import vsetup_logging
        d = int(os.environ.get('DEBUG', 0))
        if d > 0:
            vsetup_logging(10, stream=sys.stderr)
        else:
            vsetup_logging(20, stream=sys.stderr)
        vsetup_logging(log_level, logfile='', stream=sys.stderr)
    except: pass
    
    iMain(sys.argv[1:], bgui=False)
    
