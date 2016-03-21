# https://github.com/lektor/lektor/blob/master/gui/bin/make-python-framework-relocatable


PREFIX=/Users/aivar/pythonny3
LOCAL_FRAMEWORKS=$PREFIX/Thonny.app/Contents/Frameworks


VERSION=8.6

rm -rf $LOCAL_FRAMEWORKS/Tcl.framework
rm -rf $LOCAL_FRAMEWORKS/Tk.framework

mkdir -p $LOCAL_FRAMEWORKS

cp -R /Library/Frameworks/Tcl.framework $LOCAL_FRAMEWORKS
cp -R /Library/Frameworks/Tk.framework $LOCAL_FRAMEWORKS

# TODO: Make sure Versions/Current points to 8.6
rm -rf $LOCAL_FRAMEWORKS/Tcl.framework/Versions/8.5
rm -rf $LOCAL_FRAMEWORKS/Tk.framework/Versions/8.5

chmod -R u+w $PREFIX

install_name_tool -id \
	@rpath/Tcl.framework/Versions/$VERSION/Tcl \
    $LOCAL_FRAMEWORKS/Tcl.framework/Versions/$VERSION/Tcl 

install_name_tool -id \
	@rpath/Tk.framework/Versions/$VERSION/Tk \
    $LOCAL_FRAMEWORKS/Tk.framework/Versions/$VERSION/Tk 

# TODO: update executables