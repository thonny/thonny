#!/bin/bash

set -e

thonny_version=$(<../../thonny/VERSION)

#~/private/staple.sh "dist/thonny-${thonny_version}.pkg"
#~/private/staple.sh "dist/thonny-xxl-${thonny_version}.pkg"
xcrun stapler staple "dist/thonny-${thonny_version}.pkg"
