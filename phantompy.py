#!/usr/local/bin/python3.sh
# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 2; coding: utf-8 -*-
# https://gist.github.com/michaelfranzl/91f0cc13c56120391b949f885643e974/raw/a0601515e7a575bc4c7d4d2a20973b29b6c6f2df/phantom.py
"""
# phantom.py

Simple but fully scriptable headless QtWebKit browser using PyQt5 in Python3,
specialized in executing external JavaScript and generating PDF files. A lean
replacement for other bulky headless browser frameworks.


## Usage

If you have a display attached:

 ./phantom.py [--pdf_output <pdf-file>] [--js_input <javascript-file>] <url-or-html-file> 
    
If you don't have a display attached (i.e. on a remote server), you can use
xvfb-run, or don't add --show_gui - it should work without a display.

Arguments:

[--pdf_output <pdf-file>] (optional) Path and name of PDF file to generate
[--html_output <html-file>] (optional) Path and name of HTML file to generate
[--js_input <javascript-file>] (optional) Path and name of a JavaScript file to execute
--log_level 10=debug 20=info 30=warn 40=error
<url> Can be a http(s) URL or a path to a local file


## Features

* Generate a PDF screenshot of the web page after it is completely loaded.
* Optionally execute a local JavaScript file specified by the argument
   <javascript-file> after the web page is completely loaded, and before
   the PDF is generated.
* console.log's will be printed to stdout.
* Easily add new features by changing the source code of this script, without
   compiling C++ code. For more advanced applications, consider attaching
   PyQt objects/methods to WebKit's JavaScript space by using
   `QWebFrame::addToJavaScriptWindowObject()`.

If you execute an external <javascript-file>, phantom.py has no way of knowing
when that script has finished doing its work. For this reason, the external
script should execute `console.log("__PHANTOM_PY_DONE__");` when done. This will
trigger the PDF generation, after which phantom.py will exit. If no
`__PHANTOM_PY_DONE__` string is seen on the console for 10 seconds, phantom.py
will exit without doing anything. This behavior could be implemented more
elegantly without console.log's but it is the simplest solution.

It is important to remember that since you're just running WebKit, you can use
everything that WebKit supports, including the usual JS client libraries, CSS,
CSS @media types, etc.


## Dependencies

* Python3
* PyQt5
* [qasnyc](https://github.com/CabbageDevelopment/qasync) for the
  standalone program ```qasnyc_phantompy.py```

* xvfb (optional for display-less machines)

Installation of dependencies in Debian Stretch is easy:

    apt-get install xvfb python3-pyqt5 python3-pyqt5.qtwebkit
    
Finding the equivalent for other OSes is an exercise that I leave to you.


## Examples

Given the following file /tmp/test.html

    <html>
      <body>
        <p>foo <span id="id1">foo</span> <span id="id2">foo</span></p>
      </body>
      <script>
        document.getElementById('id1').innerHTML = "bar";
      </script>
    </html>
    
... and the following file /tmp/test.js:

    document.getElementById('id2').innerHTML = "baz";
    console.log("__PHANTOM_PY_DONE__");
    
... and running this script (without attached display) ...

    xvfb-run python3 phantom.py /tmp/test.html /tmp/out.pdf /tmp/test.js
    
... you will get a PDF file /tmp/out.pdf with the contents "foo bar baz".

Note that the second occurrence of "foo" has been replaced by the web page's own
script, and the third occurrence of "foo" by the external JS file.


## License

Copyright 2017 Michael Karl Franzl

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import os
import traceback
import atexit
import time

from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebEngineWidgets import QWebEnginePage

from support_phantompy import vsetup_logging

global LOG
import logging
import warnings
warnings.filterwarnings('ignore')
LOG = logging.getLogger()

def prepare(sdir='/tmp'):
    sfile = os.path.join(sdir, 'test.js')
    if not os.path.exists(sfile):
        with open(sfile, 'wt') as ofd:
            ofd.write("""
    document.getElementById('id2').innerHTML = "baz";
    console.log("__PHANTOM_PY_DONE__");
""")
    LOG.debug(f"wrote {sfile}  ")
    sfile = os.path.join(sdir, 'test.html')
    if not os.path.exists(sfile):
        with open(sfile, 'wt') as ofd:
            ofd.write("""
    <html>
      <body>
        <p>foo <span id="id1">foo</span> <span id="id2">foo</span></p>
      </body>
      <script>
        document.getElementById('id1').innerHTML = "bar";
      </script>
    </html>
""")
    LOG.debug(f"wrote {sfile}  ")
    
class Render(QWebEnginePage):
  def __init__(self, app, do_print=False, do_save=True):
    app.ldone = []
    self._app = app
    self.do_print = do_print
    self.do_save = do_save
    self.percent = 0
    self.uri = None
    self.jsfile = None
    self.htmlfile = None
    self.pdffile = None
    QWebEnginePage.__init__(self)

  def run(self, url, pdffile, htmlfile, jsfile):
    self._app.lstart.append(id(self))
    self.percent = 10
    self.uri = url
    self.jsfile = jsfile
    self.htmlfile = htmlfile
    self.pdffile = pdffile
    self.outfile = pdffile or htmlfile
    LOG.debug(f"phantom.py: URL={url} OUTFILE={outfile} JSFILE={jsfile}")
    qurl = QUrl.fromUserInput(url)    
    
    # The PDF generation only happens when the special string __PHANTOM_PY_DONE__
    # is sent to console.log(). The following JS string will be executed by
    # default, when no external JavaScript file is specified.
    self.js_contents = "setTimeout(function() { console.log('__PHANTOM_PY_DONE__') }, 5000);";
    
    if jsfile:
      try:
        with open(self.jsfile, 'rt') as f:
            self.js_contents = f.read()
      except Exception as e:
        LOG.exception(f"error reading jsfile {self.jsfile}")
        
    self.loadFinished.connect(self._loadFinished)
    self.percent = 20
    self.load(qurl)
    self.javaScriptConsoleMessage = self._onConsoleMessage
    LOG.debug(f"phantom.py: loading 10")
    
  def _onConsoleMessage(self, *args):
    if len(args) > 3:
        level, txt, lineno, filename = args
    else:
        level = 1
        txt, lineno, filename = args
    LOG.debug(f"CONSOLE {lineno} {txt} {filename}")
    if "__PHANTOM_PY_DONE__" in txt:
      self.percent = 40
      # If we get this magic string, it means that the external JS is done
      if self.do_save:
          self.toHtml(self._html_callback)
          return
      # drop through
      txt = "__PHANTOM_PY_SAVED__"
    if "__PHANTOM_PY_SAVED__" in txt:
      self.percent = 50
      if self.do_print:
          self._print()
          return
      txt = "__PHANTOM_PY_PRINTED__"
    if "__PHANTOM_PY_PRINTED__" in txt:
      self.percent = 60
      self._exit(level)
    
  def _loadFinished(self, result):
    self.percent = 30
    LOG.info(f"phantom.py: _loadFinished {result} {self.percent}")
    LOG.debug(f"phantom.py: Evaluating JS from {self.jsfile}")
    self.runJavaScript("document.documentElement.contentEditable=true")
    self.runJavaScript(self.js_contents)

  def _html_callback(self, *args):
    """print(self, QPrinter, Callable[[bool], None])"""
    if type(args[0]) is str:
        self._save(args[0])
        self._onConsoleMessage(0, "__PHANTOM_PY_SAVED__", 0 , '')
        
  def _save(self, html):
    sfile = self.htmlfile
    # CompleteHtmlSaveFormat SingleHtmlSaveFormat MimeHtmlSaveFormat
    with open(sfile, 'wt') as ofd:
        ofd.write(html)
    LOG.debug(f"Saved {sfile}")

  def _printer_callback(self, *args):
    """print(self, QPrinter, Callable[[bool], None])"""
    if args[0] is False:
        i = 1
    else:
        i = 0
    self._onConsoleMessage(i, "__PHANTOM_PY_PRINTED__", 0 , '')

  def _print(self):
    sfile = self.pdffile
    printer = QPrinter()
    printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
    printer.setPaperSize(QPrinter.A4)
    printer.setCreator("phantom.py by Michael Karl Franzl")
    printer.setOutputFormat(QPrinter.PdfFormat);
    printer.setOutputFileName(sfile)
    self.print(printer, self._printer_callback)
    LOG.debug("phantom.py: Printed")
    
  def _exit(self, val):
      self.percent = 100
      LOG.debug(f"phantom.py: Exiting with val {val}")
      # threadsafe?
      self._app.ldone.append(self.uri)

