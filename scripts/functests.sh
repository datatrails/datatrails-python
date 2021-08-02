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

export PYTHONWARNINGS="ignore:Unverified HTTPS request"
python3 -m unittest discover -v -p exec*.py -s functests
