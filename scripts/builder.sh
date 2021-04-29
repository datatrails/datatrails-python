#!/bin/sh
#
# Executes a command inside the builder container
#
# Usage Examples
#
#     ./scripts/builder.sh /bin/bash   # for shell
#     ./scripts/builder.sh             # enters python REPL
#     ./scripts/builder.sh autopep8 -i -r python # autopep8s all code

docker run \
    --rm -it \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    jitsuin-archivist-python-builder \
    "$@"
