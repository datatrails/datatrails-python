#!/bin/sh
#
# generate sbom
#
if [ "$USER" != "builder" -a "$USER" != "vscode" ]
then
    echo "Cannot run sbom.sh outside container"
    exit 0
fi

pip-audit -r requirements.txt -f cyclonedx-xml -o /tmp/sbom.xml
cat /tmp/sbom.xml | xq > docs/sbom.xml
rm /tmp/sbom.xml
