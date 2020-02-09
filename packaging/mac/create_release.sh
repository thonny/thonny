#!/bin/bash

set -e

thonny_version=$(<../../thonny/VERSION)
thonny_version="3.2.6"

echo "Releasing $thonny_version"
echo 
echo "### Creating regular installer ###############################################"
#./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt
#./sign_bundle_in_build.sh
#./create_installer_from_build.sh "thonny" "Thonny" $thonny_version

echo 
echo "### Creating XXL installer ###################################################"
./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt ../requirements-xxl-bundle.txt
./sign_bundle_in_build.sh
./create_installer_from_build.sh "thonny-xxl" "Thonny XXL" $thonny_version

echo 
echo "### Creating portable DMG ####################################################"
#./prepare_dist_bundle.sh $thonny_version ../requirements-regular-bundle.txt
#cp ../portable_thonny.ini build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin
#./sign_bundle_in_build.sh
#./create_portable_dmg_from_build.sh "thonny" $thonny_version


# Notarizing #####################################################################
# https://successfulsoftware.net/2018/11/16/how-to-notarize-your-software-on-macos/
# xcrun altool -t osx --primary-bundle-id org.thonny.Thonny --notarize-app --username <apple id email> --password <generated app specific pw> --file <dmg>
# xcrun altool --notarization-info $1 --username aivar.annamaa@gmail.com --password <notarize ID>
# xcrun stapler staple <dmg>


# clean up #######################################################################
#rm -rf build

