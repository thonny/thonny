

export REGULAR_USER=$(whoami)
export PREFIX=$HOME/pythonny_alt
export RELATIVE_LIBDIR=@executable_path/../lib

# copy files
cp /Library/Frameworks/SDL.framework/Versions/A/SDL $PREFIX/lib

cp /Library/Frameworks/SDL_image.framework/Versions/A/SDL_image $PREFIX/lib
cp /Library/Frameworks/SDL_image.framework/Versions/A/Frameworks/webp.framework/Versions/A/webp $PREFIX/lib

cp /Library/Frameworks/SDL_mixer.framework/Versions/A/SDL_mixer $PREFIX/lib
cp /Library/Frameworks/SDL_mixer.framework/Versions/A/Frameworks/FLAC.framework/Versions/A/FLAC $PREFIX/lib
cp /Library/Frameworks/SDL_mixer.framework/Versions/A/Frameworks/mikmod.framework/Versions/A/mikmod $PREFIX/lib
cp /Library/Frameworks/SDL_mixer.framework/Versions/A/Frameworks/Ogg.framework/Versions/A/Ogg $PREFIX/lib
cp /Library/Frameworks/SDL_mixer.framework/Versions/A/Frameworks/smpeg.framework/Versions/A/smpeg $PREFIX/lib
cp /Library/Frameworks/SDL_mixer.framework/Versions/A/Frameworks/Vorbis.framework/Versions/A/Vorbis $PREFIX/lib

cp /Library/Frameworks/SDL_ttf.framework/Versions/A/SDL_ttf $PREFIX/lib
cp /Library/Frameworks/SDL_ttf.framework/Versions/A/Frameworks/FreeType.framework/Versions/A/FreeType $PREFIX/lib


# update all SDL links ##########################
ls $PREFIX/lib/python3.5/site-packages/pygame/*.so | xargs -n1 install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL \
	$RELATIVE_LIBDIR/SDL  

# other links
install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL_ttf \
	$RELATIVE_LIBDIR/SDL_ttf \
	$PREFIX/lib/python3.5/site-packages/pygame/font.cpython-35m-darwin.so

	
install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL_image \
	$RELATIVE_LIBDIR/SDL_image \
	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

install_name_tool -change \
    /usr/local/lib/libjpeg.8.dylib \
	$RELATIVE_LIBDIR/libjpeg.8.dylib \
	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

#install_name_tool -change \
#    /opt/X11/lib/libpng15.15.dylib \
#	$RELATIVE_LIBDIR/libpng15.15.dylib \
#	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL_mixer \
	$RELATIVE_LIBDIR/SDL_mixer \
	$PREFIX/lib/python3.5/site-packages/pygame/mixer.cpython-35m-darwin.so

install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL_mixer \
	$RELATIVE_LIBDIR/SDL_mixer \
	$PREFIX/lib/python3.5/site-packages/pygame/mixer_music.cpython-35m-darwin.so

install_name_tool -change \
    /usr/local/opt/portmidi/lib/libportmidi.dylib \
	$RELATIVE_LIBDIR/libportmidi.dylib \
	$PREFIX/lib/python3.5/site-packages/pygame/pypm.cpython-35m-darwin.so


