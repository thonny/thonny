#!/usr/bin/env bash
set -e

# Should be run once per new Python version

# Before running this
# * Install Python (official python.org dmg). This version takes official Python installation as base

export PREFIX=$HOME/thonny_template_build_37
APP_TEMPLATE=$PREFIX/Thonny.app
export LOCAL_FRAMEWORKS=$APP_TEMPLATE/Contents/Frameworks

rm -rf $PREFIX
mkdir -p $PREFIX
cp -R -H Thonny.app.initial_template $APP_TEMPLATE

MAIN_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

$MAIN_DIR/copy_python_framework.sh

