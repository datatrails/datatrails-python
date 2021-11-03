#!/bin/sh
#
# run unittests
#
python3 --version

# run single test from cmdline for example:
#
# all tests in a module (name of file in unittest directory):
#       UNITTEST=testcompliance_policy_type task unittests
#
# all tests in a class
#       UNITTEST=testcompliance_policy_type.TestCompliancePolicyType task unittests
#
# single test
#       UNITTEST=testcompliance_policy_type.TestCompliancePolicyType.test_compliance_policy_type task unittests
#
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
${COVERAGE} annotate
${COVERAGE} html
${COVERAGE} xml
${COVERAGE} report

