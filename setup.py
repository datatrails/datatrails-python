#!/usr/bin/env python3

'''
Setup script for python build system
'''
import os
from setuptools import setup, find_packages

REPO_URL = 'https://github.com/jitsuin-inc/archivist-python/'
NAME = "jitsuin-archivist"

with open('README.md') as FF:
    DESC = FF.read()

with open('requirements.txt') as FF:
    requirements=[f"{line.strip()}" for line in FF]

setup(
    name=NAME,
    version="0.1.0alpha2",
    author="Jitsuin Inc.",
    author_email="support@jitsuin.com",
    description="Jitsuin Archivist Client",
    long_description=DESC,
    long_description_content_type="text/markdown",
    url=REPO_URL,
    packages=find_packages(exclude=( "examples", "unittests", )),
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha', #pre-delivery
        'Environment :: Console', 
        'Intended Audience :: Developers', 
        'License :: OSI Approved :: MIT License', # MIT
        'Operating System :: POSIX :: Linux', # https://pypi.org/classifiers/ # on anything
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities' # https://pypi.org/classifiers/ # check another option client-sdk
    ],
    install_requires=requirements,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'create_asset = archivist:entry.create_asset',
            'create_event = archivist:entry.create_event',
        ],
    },
)
