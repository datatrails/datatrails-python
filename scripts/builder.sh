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

docker run \
    --rm \
    -v $(pwd):/home/builder \
    -u $(id -u):$(id -g) \
    -e FUNCTEST \
    -e UNITTEST \
    -e RKVST_UNIQUE_ID \
    -e RKVST_URL \
    -e RKVST_AUTHTOKEN \
    -e RKVST_AUTHTOKEN_FILENAME \
    -e RKVST_AUTHTOKEN_FILENAME_2 \
    -e RKVST_BLOB_IDENTITY \
    -e RKVST_APPREG_CLIENT \
    -e RKVST_APPREG_SECRET \
    -e RKVST_APPREG_SECRET_FILENAME \
    -e RKVST_DEBUG \
    -e RKVST_REFRESH_TOKEN \
    -e GITHUB_REF \
    rkvst-python-builder \
    "$@"
