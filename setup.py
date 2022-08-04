#!/usr/bin/env python3

"""
Setup script for python build system
"""
import os
from setuptools import setup, find_packages

HERE = os.path.dirname(__file__)
REPO_URL = "https://github.com/jitsuin-inc/archivist-python/"
NAME = "jitsuin-archivist"

with open(os.path.join(HERE, "README.rst"), encoding="utf-8") as FF:
    DESC = FF.read()

with open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as FF:
    requirements = [f"{line.strip()}" for line in FF]

setup(
    name=NAME,
    author="RKVST Inc.",
    author_email="support@rkvst.com",
    description="RKVST Client",
    long_description=DESC,
    long_description_content_type="text/x-rst",
    url=REPO_URL,
    packages=find_packages(exclude=("examples", "unittests", "functests")),
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",  # pre-delivery
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # MIT
        "Operating System :: POSIX :: Linux",  # https://pypi.org/classifiers/ # on anything
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",  # https://pypi.org/classifiers/ # check another option client-sdk
    ],
    install_requires=requirements,
    setuptools_git_versioning={
        "template": "{tag}",
        "dev_template": "{tag}.post{ccount}+git.{sha}",
        "dirty_template": "{tag}.post{ccount}+git.{sha}.dirty",
        "version_callback": None,
        "version_file": None,
        "count_commits_from_version_file": False,
    },
    setup_requires=["setuptools-git-versioning"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "archivist_runner = archivist.cmds.runner.main:main",
            "archivist_template = archivist.cmds.template.main:main",
        ],
    },
)
