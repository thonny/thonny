#!/bin/bash

set -e

SIGN_ID="Developer ID Application: Aivar Annamaa (2SA9D4CVU8)"
CHAIN="~/Library/Keychains/login.keychain-db"

# NB! It looks like the signing order matters for notarization
# Also, it looks like any problem within the framework is also reported as problem
# with main lib (Python.framework/Versions/3.14/Python)

rm -r build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/_CodeSignature
rm -r build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/_CodeSignature
find build -name ".DS_Store" -delete

#echo "1 - libs"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	$(find build/Thonny.app -type f -name "*.so") \
	$(find build/Thonny.app -type f -name "*.dylib")

codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	$(find build/Thonny.app -type f -name "*stub?.?.a") \
	$(find build/Thonny.app -type f -name "*stub?.?.?.a")

codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	$(find build/Thonny.app -type f -name "*python.o")

codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.Framework/Versions/8.6/Tcl

codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Frameworks/Tk.Framework/Versions/8.6/Tk

codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Frameworks/Tcl.Framework
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Frameworks/Tk.Framework

#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

#echo "2 - bins"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

#echo "3 - Py.app launcher"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

#echo "4 - main lib" seems to equal to signing the framework
#codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
#	--entitlements thonny.entitlements --options runtime \
#	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

# Seems to be covered by signing Thonny.app 
#echo "5 - Py app" 
#codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
#	--entitlements thonny.entitlements --options runtime \
#	build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

# Seems to equal to signing main lib (Python.framework/Versions/3.14/Python)
#echo "6 - Framework" 
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app/Contents/Frameworks/Python.framework 
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python


echo "7 - Thonny"
codesign -s "$SIGN_ID" --force --timestamp --keychain $CHAIN \
	--entitlements thonny.entitlements --options runtime \
	build/Thonny.app
	
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Python
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/bin/python3.14
#spctl --assess -vvv build/Thonny.app/Contents/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python

