#!/bin/bash

#set -e

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"
CHAIN="~/Library/Keychains/login.keychain-db"

echo "1"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	$(find build/Thonny.app -type f -name "*.so") \
	$(find build/Thonny.app -type f -name "*.dylib") 
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "2"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7m 
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "3"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "4"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python 
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "5"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "6"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework 
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "8"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python

echo "-- 9 --"
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python
