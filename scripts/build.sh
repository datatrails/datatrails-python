#!/bin/sh
#
# Builds the container
#
# Usage Examples
#
#     ./scripts/build.sh "3.8"

if [ "$USER" = "builder" -o "$USER" = "vscode" ]
then
    echo "Cannot build container inside container"
    exit 0
fi

docker build \
    --build-arg VERSION="$1" \
    --no-cache \
    -f Dockerfile-builder \
    -t rkvst-python-builder .
