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

rm -rf rkvst-venv
python3 -m venv rkvst-venv
source rkvst-venv/bin/activate
python3 -m pip install --force-reinstall wheel
python3 -m pip install --force-reinstall dist/rkvst_archivist-*.whl
python3 -m pip install --force-reinstall -r docs/notebooks/requirements.txt
deactivate
