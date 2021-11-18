#!/bin/sh
#
# Executes a command inside the builder container
#
# Usage Examples
#
#     ./scripts/builder.sh /bin/bash   # for shell
#     ./scripts/builder.sh             # enters python REPL

docker run \
    --rm -it \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    -e UNITTEST \
    -e TEST_ARCHIVIST \
    -e TEST_AUTHTOKEN_FILENAME \
    -e TEST_DEBUG \
    jitsuin-archivist-python-builder \
    "$@"
