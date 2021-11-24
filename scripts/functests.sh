#!/bin/sh
#
# run functional tests
#
if [ -z "${TEST_ARCHIVIST}" ]
then
    echo "TEST_ARCHIVIST is undefined"
    exit 1
fi
if [ -z "${TEST_AUTHTOKEN_FILENAME}" ]
then
    echo "TEST_AUTHTOKEN_FILENAME is undefined"
    exit 1
fi
if [ ! -s "${TEST_AUTHTOKEN_FILENAME}" ]
then
    echo "${TEST_AUTHTOKEN_FILENAME} does not exist"
    exit 1
fi

python3 --version

# run single test from cmdline for example:
#
# all tests in a module (name of file in functest directory):
#       FUNCTEST=execapplications task functests
#
# all tests in a class
#       FUNCTEST=execapplications.TestApplications task functests
#
# single test
#       FUNCTEST=execapplications.TestApplications.test_appidp_token task functests
#
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
if [ -n "${FUNCTEST}" ]
then
    python3 -m unittest -v functests.${FUNCTEST}
    exit 0
fi

python3 -m unittest discover -v -p exec*.py -s functests
