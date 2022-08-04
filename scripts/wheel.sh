#!/bin/sh
#
# Builds the wheel
#
rm -rf *egg-info
rm -rf build
rm -f dist/*
python3 -m build --sdist
python3 -m build --wheel
