# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = "0.1.0"

long_description = "\n\n".join([
    open("README.md").read(),
    ])

setup(
    name="pahntompy",
    version=__version__,
    description="""A simple replacement for phantomjs using PyQt""",
    long_description=long_description,
    author="Michael Franzl (originally) Goebel",
    author_email='',
    license="1clause BSD",
    packages=['phantompy'],
    # url="",
    # These are for reference only, pip is not able to download packages
    # from github because the archives do not include the project-name.
    download_url="https://github.com/debops/yaml2rst/releases",
    keywords=['JavaScript', 'phantomjs'],
    python_requires=">=3.6",
    # probably works on PyQt6 and PySide2 but untested
    install_requires=['qasync', 'PyQt5'],
    entry_points={
        'console_scripts': [
            'phantompy = phantompy.__main__:iMain',
        ]
    },
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
