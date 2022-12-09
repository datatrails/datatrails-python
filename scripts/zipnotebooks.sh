#!/bin/sh
#
# Zips all notebooks so they can be downloaded from Sphinx-generated
# documentation.
#
INDIR=archivist/notebooks
if [ ! -d "${INDIR}" ]
then
    echo "${INDIR} does not exist"
    exit 1
fi
OUTDIR=docs/notebooks
if [ ! -d "${OUTDIR}" ]
then
    echo "${OUTDIR} does not exist"
    exit 1
fi
cp "${INDIR}"/*.ipynb "${OUTDIR}"
cd "${OUTDIR}"
rm -f notebooks.zip
zip notebooks.zip *.ipynb
