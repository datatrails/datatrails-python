#!/bin/bash
#
# run functional tests
#
if [ -z "${DATATRAILS_URL}" ]
then
    echo "DATATRAILS_URL is undefined"
    exit 1
fi
if [ -n "${DATATRAILS_APPREG_CLIENT_FILENAME}" ]
then
    if [ -s "${DATATRAILS_APPREG_CLIENT_FILENAME}" ]
    then
	export DATATRAILS_APPREG_CLIENT=$(cat ${DATATRAILS_APPREG_CLIENT_FILENAME})
    fi
fi
if [ -n "${DATATRAILS_APPREG_CLIENT}" ]
then
    if [ -n "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
    then
        if [ -s "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
        then
	    export DATATRAILS_APPREG_SECRET=$(cat ${DATATRAILS_APPREG_SECRET_FILENAME})
        fi
    fi
fi
if [ -n "${DATATRAILS_AUTHTOKEN_FILENAME}" ]
then
    if [ -s "${DATATRAILS_AUTHTOKEN_FILENAME}" ]
    then
	export DATATRAILS_AUTHTOKEN=$(cat ${DATATRAILS_AUTHTOKEN_FILENAME})
    fi
fi
if [ -z "${DATATRAILS_AUTHTOKEN}" -a -z "${DATATRAILS_APPREG_CLIENT}" -a -z "${DATATRAILS_APPREG_SECRET}" ]
then
    echo "No credentials found, DATATRAILS_AUTHTOKEN, DATATRAILS_APPREG_CLIENT,  DATATRAILS_APPREG_SECRET"
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
export DATATRAILS_ARTIST_ATTACHMENT=archivist/notebooks/test_files/pexels-andrea-turner-707697.jpeg
export DATATRAILS_UNIQUE_ID=${SRANDOM}
if [ -n "${FUNCTEST}" ]
then
    python3 -m unittest -v functests.${FUNCTEST}
    exit 0
fi

python3 -m unittest discover -v -p exec*.py -t . -s functests
