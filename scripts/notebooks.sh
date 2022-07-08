#!/bin/sh
#
# run jupyter notebooks
#
docker run --rm -it \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    -p 8888:8888 \
    -e PYTHONPATH=/home/builder \
    jitsuin-archivist-python-builder \
    jupyter notebook --ip 0.0.0.0 --no-browser --notebook-dir=/home/builder/notebooks

