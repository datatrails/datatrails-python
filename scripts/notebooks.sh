#!/bin/bash
#
# run jupyter notebooks in a virtual environment
#
# requires the datatrails-venv virtual environment to be present 
# ('task venv')

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot run notebooks.sh inside container"
    exit 0
fi

if [ ! -d datatrails-venv ]
then
    echo "venv does not exist - execute 'task venv'"
    exit 1
fi

set -x
if [ -z "${DATATRAILS_URL}" ]
then
    export DATATRAILS_URL="https://app.datatrails.ai"
fi
if [ -n "${DATATRAILS_APPREG_CLIENT_FILENAME}" ]
then
    if [ -s "${DATATRAILS_APPREG_CLIENT_FILENAME}" ]
    then
        export DATATRAILS_APPREG_CLIENT=$(cat ${DATATRAILS_APPREG_CLIENT_FILENAME})
    fi
fi
if [ -z "${DATATRAILS_APPREG_CLIENT}" ]
then
    echo "DATATRAILS_APPREG_CLIENT is not set"
    exit 1
fi
if [ -n "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
then
    if [ -s "${DATATRAILS_APPREG_SECRET_FILENAME}" ]
    then
        export DATATRAILS_APPREG_SECRET=$(cat ${DATATRAILS_APPREG_SECRET_FILENAME})
    fi
fi
if [ -z "${DATATRAILS_APPREG_SECRET}" ]
then
    echo "DATATRAILS_APPREG_SECRET is not set"
    exit 1
fi

NOTEBOOKDIR=$(pwd)/datatrails-venv/notebooks

export DATATRAILS_ARTIST_ATTACHMENT="test_files/pexels-andrea-turner-707697.jpeg"
export DATATRAILS_UNIQUE_ID=${SRANDOM}

source datatrails-venv/bin/activate
trap deactivate EXIT

mkdir -p "${NOTEBOOKDIR}"

# The customer will download the notebooks from python.datatrails.ai but
# we will copy locally
DIR=$(pwd)
cd archivist/notebooks
jupyter trust *.ipynb
cp *.ipynb "${NOTEBOOKDIR}"/
cp -r test_files "${NOTEBOOKDIR}"/
cd $DIR
jupyter notebook --help
jupyter notebook --ip 0.0.0.0 --notebook-dir="${NOTEBOOKDIR}"
