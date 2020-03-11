#!/bin/bash

set -e

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"
name_prefix=$1
version=$2

cat >build/README.txt <<EOL
This volume contains portable Thonny ${version}.

In order to use it, drag Thonny icon to your USB stick (or another location).

In portable mode Thonny keeps the configuration file inside the application bundle,
ie. Thonny remembers your settings when use your USB stick in another Mac.  .

More info about this release: https://github.com/thonny/thonny/releases/tag/v${version}
More info about Thonny: https://thonny.org
EOL


mkdir -p dist	
filename=dist/${name_prefix}-${version}-macos-portable.dmg	
rm -f $filename	
hdiutil create -srcfolder build -volname "Portable Thonny $version" -fs HFS+ -format UDBZ $filename

codesign -s "$SIGN_ID" --timestamp \
	--keychain ~/Library/Keychains/login.keychain-db \
	$filename
