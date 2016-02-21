PYTHON_SHORT_VERSION=3.5

ORIGINAL_PYTHON_FRAMEWORK=/Library/Frameworks/Python.framework/Versions/$PYTHON_SHORT_VERSION
NEW_PYTHON_EXE=$PREFIX/bin/python$PYTHON_SHORT_VERSION

cp -R $ORIGINAL_PYTHON_FRAMEWORK/* $PREFIX

# delete all Python things from bin
rm $PREFIX/bin/*

# move app version of the exe to bin
mv $PREFIX/Resources/Python.app/Contents/MacOS/Python $PREFIX/bin/python$PYTHON_SHORT_VERSION

# move main library to lib
mv $PREFIX/Python $PREFIX/lib

# clean unneccessary stuff
rm -r $PREFIX/Resources
rm -r $PREFIX/share


# Update ID-s and links
install_name_tool -id \
	$RELATIVE_LIBDIR/Python \
	$PREFIX/lib/Python
	
install_name_tool -change \
	$ORIGINAL_PYTHON_FRAMEWORK/Python \
	$RELATIVE_LIBDIR/Python \
	$NEW_PYTHON_EXE
	 