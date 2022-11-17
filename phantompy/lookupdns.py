#!/usr/local/bin/python3.sh
# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*

"""
Looks for urls https://dns.google/resolve?
https://dns.google/resolve?name=domain.name&type=TXT&cd=true&do=true
and parses them to extract a magic field.

A good example of how you can parse json embedded in HTML with phantomjs.

"""

import sys
import os

from phantompy import Render

global LOG
import logging
import warnings
warnings.filterwarnings('ignore')
LOG = logging.getLogger()

class LookFor(Render):

  def __init__(self, app, do_print=True, do_save=False):
    app.lfps = []
    self._app = app
    self.do_print = do_print
    self.do_save = do_save
    self.progress = 0
    self.we_run_this_tor_relay = None
    Render.__init__(self, app, do_print, do_save)

  def _exit(self, val):
    Render._exit(self, val)
    self.percent = 100
    LOG.debug(f"phantom.py: Exiting with val {val}")
    i = self.uri.find('name=')
    fp = self.uri[i+5:]
    i = fp.find('.')
    fp = fp[:i]
    # threadsafe?
    self._app.lfps.append(fp)

  def _html_callback(self, *args):
    """print(self, QPrinter, Callable[[bool], None])"""
    if type(args[0]) is str:
        self._save(args[0])
        i = self.ilookfor(args[0])
        self._onConsoleMessage(i, "__PHANTOM_PY_SAVED__", 0 , '')

  def ilookfor(self, html):
      import json
      marker = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
      if marker not in html: return -1
      i = html.find(marker) + len(marker)
      html = html[i:]
      assert html[0] == '{', html
      i = html.find('</pre')
      html = html[:i]
      assert html[-1] == '}', html
      LOG.debug(f"Found {len(html)} json")
      o = json.loads(html)
      if "Answer" not in o.keys() or type(o["Answer"]) != list:
          LOG.warn(f"FAIL {self.uri}")
          return 1
      for elt in o["Answer"]:
          assert type(elt) == dict, elt
          assert 'type' in elt, elt
          if elt['type'] != 16: continue
          assert 'data' in elt, elt
          if elt['data'] == 'we-run-this-tor-relay':
              LOG.info(f"OK {self.uri}")
              self.we_run_this_tor_relay = True
              return 0
      self.we_run_this_tor_relay = False
      LOG.warn(f"BAD {self.uri}")
      return 2

  def _loadFinished(self, result):
      LOG.debug(f"phantom.py: Loading finished {self.uri}")
      self.toHtml(self._html_callback)

