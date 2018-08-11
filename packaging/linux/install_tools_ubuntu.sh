#!/usr/bin/env bash

# INSTALL TOOLS #####################################################
# This is written with Ubuntu 12.04 in mind
sudo apt-get update
sudo apt-get --assume-yes upgrade
sudo apt-get --assume-yes install git mercurial # needed below
sudo apt-get --assume-yes build-dep python # probably installs too much
# https://bugs.python.org/issue31652
sudo apt-get --assume-yes install build-essential automake libtool yasm nasm \
	libncursesw5-dev libreadline6-dev libssl-dev \
	libgdbm-dev libc6-dev libsqlite3-dev tk-dev \
	libbz2-dev zlib1g-dev lzma-dev liblzma-dev xz-utils \
	libx11-dev libffi-dev uuid-dev

# lzma python-lzma

# probably some of the lzma stuff is not needed ...


