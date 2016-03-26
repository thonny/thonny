

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

cp /usr/local/lib/libjpeg.8.dylib $PREFIX/lib
cp /opt/X11/lib/libpng15.15.dylib $PREFIX/lib

# update all SDL links ##########################
ls $PREFIX/lib/python3.5/site-packages/pygame/*.so | xargs -n1 install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL \
	$RELATIVE_LIBDIR/SDL  

find $PREFIX/lib -maxdepth 1 | xargs -n1 install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL \
	$RELATIVE_LIBDIR/SDL  

# other links
install_name_tool -change \
    @rpath/SDL.framework/Versions/A/SDL_ttf \
	$RELATIVE_LIBDIR/SDL_ttf \
	$PREFIX/lib/python3.5/site-packages/pygame/font.cpython-35m-darwin.so

	
install_name_tool -id \
	$RELATIVE_LIBDIR/SDL_image \
	$PREFIX/lib/SDL_image
	
install_name_tool -id \
	$RELATIVE_LIBDIR/SDL_ttf \
	$PREFIX/lib/SDL_ttf
	
install_name_tool -id \
	$RELATIVE_LIBDIR/SDL_mixer \
	$PREFIX/lib/SDL_mixer
	
install_name_tool -id \
	$RELATIVE_LIBDIR/SDL \
	$PREFIX/lib/SDL
	
install_name_tool -id \
	$RELATIVE_LIBDIR/FLAC \
	$PREFIX/lib/FLAC

install_name_tool -id \
	$RELATIVE_LIBDIR/Ogg \
	$PREFIX/lib/Ogg

install_name_tool -id \
	$RELATIVE_LIBDIR/smpeg \
	$PREFIX/lib/smpeg

install_name_tool -id \
	$RELATIVE_LIBDIR/mikmod \
	$PREFIX/lib/mikmod

install_name_tool -id \
	$RELATIVE_LIBDIR/Vorbis \
	$PREFIX/lib/Vorbis

install_name_tool -id \
	$RELATIVE_LIBDIR/FreeType \
	$PREFIX/lib/FreeType

install_name_tool -id \
	$RELATIVE_LIBDIR/Ogg \
	$PREFIX/lib/Ogg

install_name_tool -id \
	$RELATIVE_LIBDIR/webp \
	$PREFIX/lib/webp
		
install_name_tool -id \
	$RELATIVE_LIBDIR/webp \
	$PREFIX/lib/webp
		
install_name_tool -change \
    @rpath/webp.framework/Versions/A/webp \
	$RELATIVE_LIBDIR/webp \
	$PREFIX/lib/SDL_image

install_name_tool -change \
    @rpath/FreeType.framework/Versions/A/FreeType \
	$RELATIVE_LIBDIR/FreeType \
	$PREFIX/lib/SDL_ttf

install_name_tool -change \
    @rpath/Ogg.framework/Versions/A/Ogg \
	$RELATIVE_LIBDIR/Ogg \
	$PREFIX/lib/FLAC

install_name_tool -change \
    @rpath/Ogg.framework/Versions/A/Ogg \
	$RELATIVE_LIBDIR/Ogg \
	$PREFIX/lib/Vorbis

install_name_tool -change \
    @rpath/mikmod.framework/Versions/A/mikmod \
	$RELATIVE_LIBDIR/mikmod \
	$PREFIX/lib/SDL_mixer

install_name_tool -change \
    @rpath/smpeg.framework/Versions/A/smpeg \
	$RELATIVE_LIBDIR/smpeg \
	$PREFIX/lib/SDL_mixer

install_name_tool -change \
    @rpath/Ogg.framework/Versions/A/Ogg \
	$RELATIVE_LIBDIR/Ogg \
	$PREFIX/lib/SDL_mixer

install_name_tool -change \
    @rpath/Vorbis.framework/Versions/A/Vorbis \
	$RELATIVE_LIBDIR/Vorbis \
	$PREFIX/lib/SDL_mixer

install_name_tool -change \
    @rpath/FLAC.framework/Versions/A/FLAC \
	$RELATIVE_LIBDIR/FLAC \
	$PREFIX/lib/SDL_mixer

install_name_tool -change \
    @rpath/SDL_image.framework/Versions/A/SDL_image \
	$RELATIVE_LIBDIR/SDL_image \
	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

install_name_tool -change \
    /usr/local/lib/libjpeg.8.dylib \
	$RELATIVE_LIBDIR/libjpeg.8.dylib \
	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

# TODO: is it necessary? XQuartz will provide libpng anyway ...
install_name_tool -change \
    /opt/X11/lib/libpng15.15.dylib \
	$RELATIVE_LIBDIR/libpng15.15.dylib \
	$PREFIX/lib/python3.5/site-packages/pygame/imageext.cpython-35m-darwin.so

install_name_tool -change \
    @rpath/SDL_mixer.framework/Versions/A/SDL_mixer \
	$RELATIVE_LIBDIR/SDL_mixer \
	$PREFIX/lib/python3.5/site-packages/pygame/mixer.cpython-35m-darwin.so

install_name_tool -change \
    @rpath/SDL_mixer.framework/Versions/A/SDL_mixer \
	$RELATIVE_LIBDIR/SDL_mixer \
	$PREFIX/lib/python3.5/site-packages/pygame/mixer_music.cpython-35m-darwin.so

install_name_tool -change \
    /usr/local/opt/portmidi/lib/libportmidi.dylib \
	$RELATIVE_LIBDIR/libportmidi.dylib \
	$PREFIX/lib/python3.5/site-packages/pygame/pypm.cpython-35m-darwin.so

install_name_tool -change \
    @rpath/SDL_ttf.framework/Versions/A/SDL_ttf \
	$RELATIVE_LIBDIR/SDL_ttf \
	$PREFIX/lib/python3.5/site-packages/pygame/font.cpython-35m-darwin.so


