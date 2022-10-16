#!/bin/sh
#
# run jupyter notebooks
#

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot run notebooks.sh inside container"
    exit 0
fi

docker run --rm -it \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    -p 8888:8888 \
    -e PYTHONPATH=/home/builder \
    jitsuin-archivist-python-builder \
    jupyter notebook --ip 0.0.0.0 --no-browser --notebook-dir=/home/builder/notebooks

