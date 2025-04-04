#!/bin/bash
#
# run unittests
#
python3 --version

# run single test from cmdline for example:
#
# all tests in a module (name of file in unittest directory):
#       UNITTEST=testRunnerstep task unittests
#
# all tests in a class
#       UNITTEST=testrunnerstep.TestRunnerStep task unittests
#
# single test
#       UNITTEST=testrunnerstep.TestRunnerStep.test_runner_step task unittests
#
export DATATRAILS_ARTIST_ATTACHMENT=archivist/notebooks/test_files/pexels-andrea-turner-707697.jpeg
export DATATRAILS_UNIQUE_ID=${SRANDOM}
if [ -n "${UNITTEST}" ]
then
    python3 -m unittest -v unittests.${UNITTEST}
    exit 0
fi


rm -f coverage.xml
rm -rf htmlcov
COVERAGE="coverage"
${COVERAGE} --version
${COVERAGE} run --branch --source archivist -m unittest -v 
${COVERAGE} html
${COVERAGE} xml
${COVERAGE} report

