#!/bin/sh
#
# Shells into the builder container
#

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    "$@"
    exit 0
fi

set -x
# If no arguments simply shell into builder image
docker run \
    --rm -it \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    rkvst-python-builder \
    "/bin/bash"
