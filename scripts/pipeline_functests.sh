#!/bin/bash
#
# run functests with xml reporting

rm -rf functest-results
mkdir -p functest-results
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
export DATATRAILS_ARTIST_ATTACHMENT=archivist/notebooks/test_files/pexels-andrea-turner-707697.jpeg
export DATATRAILS_UNIQUE_ID=${SRANDOM}
python -m xmlrunner discover -v -p exec*.py -t . -s functests -o ./functest-results/
exit 0
