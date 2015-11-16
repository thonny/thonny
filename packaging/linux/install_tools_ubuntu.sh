#!/usr/bin/env bash

# INSTALL TOOLS #####################################################
# This is written with Ubuntu 12.04 in mind
sudo apt-get update
sudo apt-get upgrade
sudo apt-get --assume-yes install git mercurial # needed below
sudo apt-get --assume-yes build-dep python # probably installs too much
sudo apt-get --assume-yes install build-essential libncursesw5-dev libreadline6-dev libssl-dev libgdbm-dev libc6-dev libsqlite3-dev tk-dev libbz2-dev lzma-dev liblzma-dev python-lzma lzma xz-utils xz-lzma
# probably some of the lzma stuff is not needed ...


