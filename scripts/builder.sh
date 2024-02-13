#!/bin/sh
#
# Executes a command inside the builder container
#
# Usage Examples
#
#     ./scripts/builder.sh /bin/bash   # for shell
#     ./scripts/builder.sh             # enters python REPL

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    "$@"
    exit 0
fi

if [ -t 1 ]
then
    USE_TTY="-it"
fi

docker run \
    --rm ${USE_TTY} \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    -e FUNCTEST \
    -e UNITTEST \
    -e DATATRAILS_UNIQUE_ID \
    -e DATATRAILS_URL \
    -e DATATRAILS_AUTHTOKEN \
    -e DATATRAILS_AUTHTOKEN_FILENAME \
    -e DATATRAILS_AUTHTOKEN_FILENAME_2 \
    -e DATATRAILS_BLOB_IDENTITY \
    -e DATATRAILS_APPREG_CLIENT \
    -e DATATRAILS_APPREG_SECRET \
    -e DATATRAILS_APPREG_SECRET_FILENAME \
    -e DATATRAILS_LOGLEVEL \
    -e DATATRAILS_REFRESH_TOKEN \
    -e GITHUB_REF \
    datatrails-python-builder \
    "$@"


