#!/bin/bash
#
# run jupyter notebooks in a virtual environment
#
# requires the rkvst-venv virtual environment to be present 
# ('task venv')

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot run notebooks.sh inside container"
    exit 0
fi

if [ ! -d rkvst-venv ]
then
    echo "venv does not exist - execute 'task venv'"
    exit 1
fi

NOTEBOOKDIR=rkvst-venv/notebooks

export RKVST_ARTIST_ATTACHMENT="test_files/pexels-andrea-turner-707697.jpeg"
export RKVST_UNIQUE_ID=${SRANDOM}

source rkvst-venv/bin/activate
mkdir -p "${NOTEBOOKDIR}"

# The customer will download the notebooks from python.rkvst.com but
# we will copy locally
cp archivist/notebooks/*.ipynb "${NOTEBOOKDIR}"/
cp -r archivist/notebooks/test_files "${NOTEBOOKDIR}"/
jupyter notebook --ip 0.0.0.0 --notebook-dir="${NOTEBOOKDIR}"
deactivate
