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
    -e FUNCTEST \
    -e UNITTEST \
    -e ARCHIVIST_NAMESPACE \
    -e TEST_ARCHIVIST \
    -e TEST_AUTHTOKEN \
    -e TEST_AUTHTOKEN_FILENAME \
    -e TEST_AUTHTOKEN_FILENAME_2 \
    -e TEST_CLIENT_ID \
    -e TEST_CLIENT_SECRET \
    -e TEST_CLIENT_SECRET_FILENAME \
    -e TEST_DEBUG \
    -e TEST_REFRESH_TOKEN \
    jitsuin-archivist-python-builder \
    "$@"
