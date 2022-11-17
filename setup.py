# -*-mode: python; indent-tabs-mode: nil; py-indent-offset: 4; coding: utf-8 -*

import re
from setuptools import setup

with open("qasync/__init__.py") as f:
    version = re.search(r'__version__\s+=\s+"(.*)"', f.read()).group(1)

long_description = "\n\n".join([
    open("README.md").read(),
    ])

if __name__ == '__main__':
    setup(
        name="phantompy",
        version=__version__,
        description="""A simple replacement for phantomjs using PyQt""",
        long_description=long_description,
        author="Michael Franzl (originally)",
        author_email='',
        license="1clause BSD",
        packages=['phantompy'],
        # url="",
        # download_url="https://",
        keywords=['JavaScript', 'phantomjs', 'asyncio'],
        # maybe less - nothing fancy
        python_requires="~=3.6",
        # probably works on PyQt6 and PySide2 but untested
        # https://github.com/CabbageDevelopment/qasync/
        install_requires=['qasync', 'PyQt5'],
        entry_points={
            'console_scripts': ['phantompy = phantompy.__main__:iMain', ]},
        classifiers=[
                     'Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Web Developers',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 3',
                     'Topic :: Software Development :: Documentation',
                     ],
                     )
