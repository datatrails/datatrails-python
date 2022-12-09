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

NOTEBOOKDIR=rkvst-venv/notebooks

source rkvst-venv/bin/activate
mkdir -p "${NOTEBOOKDIR}"

# The customer will download the notebooks from python.rkvst.com but
# we will copy locally
cp archivist/notebooks/*.ipynb "${NOTEBOOKDIR}"/
jupyter notebook --ip 0.0.0.0 --notebook-dir="${NOTEBOOKDIR}"
deactivate
