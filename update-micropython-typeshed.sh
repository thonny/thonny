#!/usr/bin/env bash

TARGET=thonny/plugins/micropython/_temp

rm -rf $TARGET
pip3 install --upgrade --target $TARGET micropython-unix-stubs
pip3 install --upgrade --target $TARGET micropython-samd-stubs
pip3 install --upgrade --target $TARGET micropython-stm32-stubs
pip3 install --upgrade --target $TARGET micropython-esp8266-stubs
pip3 install --upgrade --target $TARGET micropython-esp32-stubs
pip3 install --upgrade --target $TARGET micropython-rp2-stubs
#pip3 install --upgrade --target $TARGET micropython-stdlib-stubs

# TODO: copy selected files and delete _temp
