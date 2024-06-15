#!/bin/bash

set -e

thonny_version=$(<../../thonny/VERSION)

echo "Releasing $thonny_version"
echo 
echo "### Creating regular installer ###############################################"
./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt
echo "--- Signing -------------------------------------"
./sign_bundle_in_build.sh
echo "--- Creating installer -------------------------------------"
./create_installer_from_build.sh "thonny" "Thonny" $thonny_version

echo 
# clean up #######################################################################
#rm -rf build

