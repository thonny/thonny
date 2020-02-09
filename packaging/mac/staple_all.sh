#!/bin/bash

thonny_version=$(<../../thonny/VERSION)
thonny_version="3.2.6"

~/private/staple.sh "dist/thonny-${thonny_version}-macos-installer.pkg"
~/private/staple.sh "dist/thonny-${thonny_version}-macos-portable.dmg"
#~/private/staple.sh "dist/thonny-xxl-${thonny_version}-macos-installer.pkg"
