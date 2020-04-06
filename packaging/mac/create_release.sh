#!/bin/bash

set -e

thonny_version=$(<../../thonny/VERSION)

echo "Releasing $thonny_version"
echo 
echo "### Creating regular installer ###############################################"
./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt
./sign_bundle_in_build.sh
./create_installer_from_build.sh "thonny" "Thonny" $thonny_version

echo 
echo "### Creating XXL installer ###################################################"
./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt ../requirements-xxl-bundle.txt
./sign_bundle_in_build.sh
./create_installer_from_build.sh "thonny-xxl" "Thonny XXL" $thonny_version

#echo 
#echo "### Creating portable DMG ####################################################"
#./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt
#cp ../portable_thonny.ini build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin
#./sign_bundle_in_build.sh
#./create_portable_dmg_from_build.sh "thonny" $thonny_version


# clean up #######################################################################
#rm -rf build

