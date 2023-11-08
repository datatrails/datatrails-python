#!/bin/bash
#
# run functional tests
#
if [ -z "${DATATRAILS_URL}" ]
then
    echo "DATATRAILS_URL is undefined"
    exit 1
fi
if [ -n "${DATATRAILS_APPREG_CLIENT}" ]
then
    if [ -n "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
    then
        if [ ! -s "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
        then
            echo "${DATATRAILS_APPREG_SECRET_FILENAME} does not exist"
            exit 1
        fi
    elif [ -z "${DATATRAILS_APPREG_SECRET}" ]
    then
        echo "Both DATATRAILS_APPREG_SECRET_FILENAME"
        echo "and DATATRAILS_APPREG_SECRET are undefined"
        exit 1
    fi
else
    if [ -n "${DATATRAILS_AUTHTOKEN_FILENAME}" ]
    then
        if [ ! -s "${DATATRAILS_AUTHTOKEN_FILENAME}" ]
        then
            echo "${DATATRAILS_AUTHTOKEN_FILENAME} does not exist"
            exit 1
        fi
    elif [ -z "${DATATRAILS_AUTHTOKEN}" ]
    then
        echo "Both DATATRAILS_AUTHTOKEN_FILENAME"
        echo "and DATATRAILS_AUTHTOKEN are undefined"
        exit 1
    fi
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
export DATATRAILS_ARTIST_ATTACHMENT=archivist/notebooks/test_files/pexels-andrea-turner-707697.jpeg
export DATATRAILS_UNIQUE_ID=${SRANDOM}
if [ -n "${FUNCTEST}" ]
then
    python3 -m unittest -v functests.${FUNCTEST}
    exit 0
fi

python3 -m unittest discover -v -p exec*.py -t . -s functests
