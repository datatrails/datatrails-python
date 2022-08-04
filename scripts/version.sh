#!/bin/sh
#
# inserts version into python package
#
version=$(git describe --tags --long --dirty)

cat > archivist/about.py <<EOF
"""Archivist SDK

   WARNING: Do **not** edit directly
   This file is auto-generated by ./scripts/version.sh and is
   not version controlled by git (ironically) as this would
   make the generated version from the tag 'dirty'
"""
__version__ = "$version"
EOF
