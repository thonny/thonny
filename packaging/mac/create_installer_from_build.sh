#!/bin/bash
set -e

VERSION=$1
PROD_PKG_PREFIX=$2

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"
INSTALLER_SIGN_ID="Developer ID Installer: Aivar Annamaa (2SA9D4CVU8)"

codesign -s "$SIGN_ID" --force --deep --timestamp --keychain ~/Library/Keychains/login.keychain-db \
	--entitlements thonny.entitlements \
	$(find build/Thonny.app -type f -name "*.so") \
	$(find build/Thonny.app -type f -name "*.dylib") 

codesign -s "$SIGN_ID" --force --timestamp --keychain ~/Library/Keychains/login.keychain-db \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app 

# For some reason this executable needs to be signed after the others, 
# otherwise notarizer reports it as with invalid signature
codesign -s "$SIGN_ID" --force --timestamp --keychain ~/Library/Keychains/login.keychain-db \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python 
	
codesign -s "$SIGN_ID" --force --timestamp --keychain ~/Library/Keychains/login.keychain-db \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app

# create installer ################
# prepare resources
echo "Creating installer"
rm -rf resources_build
mkdir  resources_build
cp resource_templates/* resources_build
sed -i '' "s/VERSION/$VERSION/g" resources_build/WELCOME.html
cp ../license-soft-wrap.txt resources_build/LICENSE.txt

echo "Creating component package"
# component
COMPONENT_PACKAGE=ThonnyComponent.pkg
rm -f $COMPONENT_PACKAGE
pkgbuild \
 	--root build \
	--component-plist Component.plist \
	--install-location /Applications\
	--scripts scripts \
	--identifier "org.thonny.Thonny.component" \
	--version $VERSION \
	--filter readme.txt \
	--sign "$INSTALLER_SIGN_ID" \
	--keychain ~/Library/Keychains/login.keychain-db \
	--timestamp \
	$COMPONENT_PACKAGE
	
echo "Creating product archive"
PRODUCT_ARCHIVE=dist/${PROD_PKG_PREFIX}-${VERSION}.pkg
rm -f $PRODUCT_ARCHIVE
productbuild \
	--identifier "org.thonny.Thonny.product" \
	--version $VERSION \
	--distribution Distribution.plist \
	--resources resources_build \
	--sign "$INSTALLER_SIGN_ID" \
	--keychain ~/Library/Keychains/login.keychain-db \
	--timestamp \
	$PRODUCT_ARCHIVE
