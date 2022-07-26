#!/bin/sh
#
# Builds the container
#
# Usage Examples
#
#     ./scripts/build.sh "3.7"

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot build container inside container"
    exit 0
fi

docker build \
    --no-cache \
    --build-arg VERSION="$1" \
    -f Dockerfile-builder \
    -t jitsuin-archivist-python-builder .
