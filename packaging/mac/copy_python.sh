PYTHON_SHORT_VERSION=3.5

ORIGINAL_PYTHON_FRAMEWORK=/Library/Frameworks/Python.framework/Versions/$PYTHON_SHORT_VERSION
NEW_PYTHON_EXE=$PREFIX/bin/python$PYTHON_SHORT_VERSION

cp -R $ORIGINAL_PYTHON_FRAMEWORK/* $PREFIX

# delete all Python things from bin
rm $PREFIX/bin/*

# move app version of the exe to bin
mv $PREFIX/Resources/Python.app/Contents/MacOS/Python $PREFIX/bin/python$PYTHON_SHORT_VERSION

# move main library to lib and update soft links
mv $PREFIX/Python $PREFIX/lib

cd $PREFIX/lib
rm libpython3.5.dylib
rm libpython3.5m.dylib
ln -s Python libpython3.5.dylib
ln -s Python libpython3.5m.dylib

cd $PREFIX/lib/python3.5/config-3.5m
rm libpython3.5.dylib
rm libpython3.5m.dylib
rm libpython3.5.a
rm libpython3.5m.a
ln -s ../../Python libpython3.5.dylib
ln -s ../../Python libpython3.5m.dylib
ln -s ../../Python libpython3.5.a
ln -s ../../Python libpython3.5m.a

cd $TEMP_BUILD_DIR


#######################################################################################
# Update ID-s and links

install_name_tool -id \
	$RELATIVE_LIBDIR/Python \
	$PREFIX/lib/Python
	
install_name_tool -change \
	$ORIGINAL_PYTHON_FRAMEWORK/Python \
	$RELATIVE_LIBDIR/Python \
	$NEW_PYTHON_EXE

PYTHON_FRAMEWORK_LIBDIR=/Library/Frameworks/Python.framework/Versions/3.5/lib

install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/readline.cpython-35m-darwin.so
    
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libpanelw.5.dylib \
	$RELATIVE_LIBDIR/libpanelw.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_curses_panel.cpython-35m-darwin.so
    
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_curses_panel.cpython-35m-darwin.so
    
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/python3.5/lib-dynload/_curses.cpython-35m-darwin.so
    
# dylibs dependent on libncursesw
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/libformw.5.dylib
                
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/libpanelw.5.dylib
                
install_name_tool -change \
    $PYTHON_FRAMEWORK_LIBDIR/libncursesw.5.dylib \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/libmenuw.5.dylib
    

# ID-s for libncurses things
install_name_tool -id \
	$RELATIVE_LIBDIR/libformw.5.dylib \
    $PREFIX/lib/libformw.5.dylib
                
install_name_tool -id \
	$RELATIVE_LIBDIR/libpanelw.5.dylib \
    $PREFIX/lib/libpanelw.5.dylib
                
install_name_tool -id \
	$RELATIVE_LIBDIR/libmenuw.5.dylib \
    $PREFIX/lib/libmenuw.5.dylib
                
install_name_tool -id \
	$RELATIVE_LIBDIR/libncursesw.5.dylib \
    $PREFIX/lib/libncursesw.5.dylib
                
