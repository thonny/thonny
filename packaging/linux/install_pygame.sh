#!/usr/bin/env bash

#http://www.pygame.org/wiki/CompileUbuntu
#install dependencies
sudo apt-get  --assume-yes install \
	mercurial python3-dev python3-numpy libav-tools \
    	libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev \
	libsmpeg-dev libsdl1.2-dev  libportmidi-dev libswscale-dev \
	libavformat-dev libavcodec-dev freepats
 
# Grab source
hg clone https://bitbucket.org/pygame/pygame
 
# Finally build and install
cd pygame
$PREFIX/bin/python3.5 setup.py build
$PREFIX/bin/python3.5 setup.py install

cd ..
