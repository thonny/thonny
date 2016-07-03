# https://github.com/lektor/lektor/blob/master/gui/bin/make-python-framework-relocatable


# Take from environment
#LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks

VERSION=8.5
WRONG_VERSION=8.6

rm -rf $LOCAL_FRAMEWORKS/Tcl.framework
rm -rf $LOCAL_FRAMEWORKS/Tk.framework

mkdir -p $LOCAL_FRAMEWORKS

# TODO: Make sure Versions/Current points to $VERSION

cp -R /Library/Frameworks/Tcl.framework $LOCAL_FRAMEWORKS
cp -R /Library/Frameworks/Tk.framework $LOCAL_FRAMEWORKS

# remove other version
rm -rf $LOCAL_FRAMEWORKS/Tcl.framework/Versions/$WRONG_VERSION
rm -rf $LOCAL_FRAMEWORKS/Tk.framework/Versions/$WRONG_VERSION

chmod -R u+w $LOCAL_FRAMEWORKS/Tcl.framework # TODO: make only selected items writable or remove the permission later
chmod -R u+w $LOCAL_FRAMEWORKS/Tk.framework

install_name_tool -id \
	@rpath/Tcl.framework/Versions/$VERSION/Tcl \
    $LOCAL_FRAMEWORKS/Tcl.framework/Versions/$VERSION/Tcl 

install_name_tool -id \
	@rpath/Tk.framework/Versions/$VERSION/Tk \
    $LOCAL_FRAMEWORKS/Tk.framework/Versions/$VERSION/Tk 

# TODO: update executables