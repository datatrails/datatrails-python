#!/bin/bash
#
# recreate virtual environment
#
# requires the wheel to be present in dist/ (execute 'task wheel')

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot run notebooks.sh inside container"
    exit 0
fi

if [ ! -s dist/datatrails_archivist-*.whl ]
then
    echo "no wheel found - execute 'task wheel'"
    exit 1
fi

rm -rf datatrails-venv
python3 -m venv datatrails-venv
source datatrails-venv/bin/activate
trap deactivate EXIT
python3 -m pip install --force-reinstall wheel
python3 -m pip install --force-reinstall dist/datatrails_archivist-*.whl
python3 -m pip install --force-reinstall -r docs/notebooks/requirements.txt
