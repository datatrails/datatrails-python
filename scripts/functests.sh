#!/bin/bash
#
# run functional tests
#
if [ -z "${RKVST_URL}" ]
then
    echo "RKVST_URL is undefined"
    exit 1
fi
if [ -n "${RKVST_APPREG_CLIENT}" ]
then
    if [ -n "${RKVST_APPREG_SECRET_FILENAME}" ]
    then
        if [ ! -s "${RKVST_APPREG_SECRET_FILENAME}" ]
        then
            echo "${RKVST_APPREG_SECRET_FILENAME} does not exist"
            exit 1
        fi
    elif [ -z "${RKVST_APPREG_SECRET}" ]
    then
        echo "Both RKVST_APPREG_SECRET_FILENAME"
        echo "and RKVST_APPREG_SECRET are undefined"
        exit 1
    fi
else
    if [ -n "${RKVST_AUTHTOKEN_FILENAME}" ]
    then
        if [ ! -s "${RKVST_AUTHTOKEN_FILENAME}" ]
        then
            echo "${RKVST_AUTHTOKEN_FILENAME} does not exist"
            exit 1
        fi
    elif [ -z "${RKVST_AUTHTOKEN}" ]
    then
        echo "Both RKVST_AUTHTOKEN_FILENAME"
        echo "and RKVST_AUTHTOKEN are undefined"
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
export RKVST_ARTIST_ATTACHMENT=archivist/notebooks/test_files/pexels-andrea-turner-707697.jpeg
export RKVST_UNIQUE_ID=${SRANDOM}
if [ -n "${FUNCTEST}" ]
then
    python3 -m unittest -v functests.${FUNCTEST}
    exit 0
fi

python3 -m unittest discover -v -p exec*.py -t . -s functests
