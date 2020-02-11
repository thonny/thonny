#!/bin/bash

set -e

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"
CHAIN="~/Library/Keychains/login.keychain-db"

# NB! It looks like the signing order matters for notarization
# Also, it looks like any problem within the framework is also reported as problem
# with main lib (Python.framework/Versions/3.7/Python)

#echo "1 - libs"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	$(find build/Thonny.app -type f -name "*.so") \
	$(find build/Thonny.app -type f -name "*.dylib") 
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

#echo "2 - bins"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7m 
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

#echo "3 - Py.app launcher"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

#echo "4 - main lib" seems to equal to signing the framework
#codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
#	--entitlements thonny.entitlements --options runtime \
#	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python 
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

# Seems to be covered by signing Thonny.app 
#echo "5 - Py app" 
#codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
#	--entitlements thonny.entitlements --options runtime \
#	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

# Seems to equal to signing main lib (Python.framework/Versions/3.7/Python)
#echo "6 - Framework" 
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework 
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python


#echo "7 - Thonny" 
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app
	
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.7/Resources/Python.app/Contents/MacOS/Python

