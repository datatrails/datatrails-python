#!/bin/sh
#
# run unittests
#

rm -f coverage.xml
rm -rf htmlcov
COVERAGE="coverage"
${COVERAGE} --version
${COVERAGE} run --branch --source archivist -m unittest discover -v
${COVERAGE} annotate
${COVERAGE} html
${COVERAGE} xml
${COVERAGE} report
