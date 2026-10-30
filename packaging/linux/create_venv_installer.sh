#!/bin/bash

set -e

VERSION=$(<../../thonny/VERSION)
DOWNINSTALL_FILENAME=thonny-${VERSION}.bash
DOWNINSTALL_TARGET=dist/$DOWNINSTALL_FILENAME
cp venv_install_template.sh $DOWNINSTALL_TARGET
sed -i.bak "s/_VERSION_/${VERSION}/g" "$DOWNINSTALL_TARGET"
rm "$DOWNINSTALL_TARGET.bak"
./insert_deps.py ../requirements-regular-bundle.txt $DOWNINSTALL_TARGET
