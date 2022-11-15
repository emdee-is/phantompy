# phantompy

A simple replacement for phantomjs using PyQt. 

This code is based on a brilliant idea of
[Michael Franzl](https://gist.github.com/michaelfranzl/91f0cc13c56120391b949f885643e974/raw/a0601515e7a575bc4c7d4d2a20973b29b6c6f2df/phantom.py)
that he wrote up in his
[blog](https://blog.michael.franzl.name/2017/10/16/phantom-py/index.html)

## Features

* Generate a PDF screenshot of the web page after it is completely loaded.
* Optionally execute a local JavaScript file specified by the argument
```javascript-file``` after the web page is completely loaded, and before the
 PDF is generated. (YMMV - it segfaults for me. )
* Generate a HTML save file screenshot of the web page after it is
  completely loaded and the javascript has run.
* console.log’s will be printed to stdout.
* Easily add new features by changing the source code of this script,
 without compiling C++ code. For more advanced applications, consider
 attaching PyQt objects/methods to WebKit’s JavaScript space by using
 QWebFrame::addToJavaScriptWindowObject().

If you execute an external ```javascript-file```, phantompy has no
way of knowing when that script has finished doing its work. For this
reason, the external script should execute at the end
```console.log("__PHANTOM_PY_DONE__");``` when done. This will trigger
the PDF generation or the file saving, after which phantompy will exit.

If no ```__PHANTOM_PY_DONE__``` string is seen on the console for 10
seconds, phantom.py will exit without doing anything. This behavior
could be implemented more elegantly without console.log’s but it is
the simplest solution.

It is important to remember that since you’re just running WebKit, you can
use everything that WebKit supports, including the usual JS client
libraries, CSS, CSS @media types, etc.

## Dependencies

* Python3
* PyQt5 (this should work with PySide2 and PyQt6 - let us know.)
* [qasyc](https://github.com/CabbageDevelopment/qasync) for the
  standalone program ```qasync_lookup.py```

## Standalone

A standalone program is a little tricky as PyQt PyQt5.QtWebEngineWidgets'
QWebEnginePage uses callbacks at each step of the way:
1) loading the page = ```Render.run```
2) running javascript in and on the page = ```Render._loadFinished```
3) saving the page = ```Render.toHtml and _html_callback```
4) printing the page = ```Render._print```

The steps get chained by printing special messages to the Python
renderer of the JavaScript console: ```Render. _onConsoleMessage```

So it makes it hard if you want the standalone program to work without
a GUI, or in combination with another Qt program that is responsible
for the PyQt ```app.exec``` and the exiting of the program.

We've decided to use the best of the shims that merge the Python
```asyncio``` and Qt event loops:
[qasyc](https://github.com/CabbageDevelopment/qasync). This is seen as
the successor to the sorta abandonned[](https://github.com/harvimt/quamash).
The code is based on a
[comment](https://github.com/CabbageDevelopment/qasync/issues/35#issuecomment-1315060043)
by [Alex Marcha](https://github.com/hosaka) who's excellent code helped me.
As this is my first use of ```asyncio``` and ```qasync``` I may have
introduced some errors and it may be improved on, but it works, and
it not a monolithic Qt program.

## Usage

The standalone program is ```quash_phantompy.py```


### Arguments

```
<url> Can be a http(s) URL or a path to a local file
<pdf-file> Path and name of PDF file to generate
[<javascript-file>] (optional) Path and name of a JavaScript file to execute
```


## Postscript

When I think of all the trouble people went to compiling and
maintaining the tonnes of C++ code that went into
[phantomjs](https://github.com/ariya/phantomjs), I am amazed that it
can be replaced with a couple of hundred lines of Python!

