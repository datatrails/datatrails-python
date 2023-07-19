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
rm ${OUTDIR}/*.ipynb
rm -rf ${OUTDIR}/test_files
cp -r "${INDIR}"/*.ipynb "${INDIR}"/test_files "${OUTDIR}"
cd "${OUTDIR}"
rm -f notebooks.zip
zip -r notebooks.zip *.ipynb test_files
