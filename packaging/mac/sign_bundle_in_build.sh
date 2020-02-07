#!/bin/bash

set -e

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"

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
