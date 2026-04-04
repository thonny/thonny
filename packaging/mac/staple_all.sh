#!/bin/bash

set -e

thonny_version=$(<../../thonny/VERSION)

xcrun stapler staple "dist/thonny-${thonny_version}.pkg"
