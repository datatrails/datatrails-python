#!/bin/sh
#
# run functests with xml reporting

rm -rf functest-results
mkdir -p functest-results
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
python -m xmlrunner discover -v -p exec*.py -s functests -o ./functest-results/