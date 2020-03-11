#!/bin/bash
set -e

PROD_PKG_PREFIX=$1
PROD_NAME=$2
VERSION=$3

INSTALLER_SIGN_ID="Developer ID Installer: Aivar Annamaa (2SA9D4CVU8)"

# prepare resources
echo "Creating installer"
rm -rf resources_build
mkdir  resources_build
cp resource_templates/* resources_build
sed -i '' "s/VERSION/$VERSION/g" resources_build/WELCOME.html
sed -i '' "s/PROD_NAME/$PROD_NAME/g" resources_build/WELCOME.html
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
