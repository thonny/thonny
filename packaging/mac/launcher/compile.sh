#!/bin/zsh

swiftc -target x86_64-apple-macosx10.9 -o launcher_x86 launcher.swift
swiftc -target arm64-apple-macosx11.0 -o launcher_arm launcher.swift

lipo -create -output ../Thonny.app.initial_template/Contents/MacOS/thonny launcher_x86 launcher_arm

rm launcher_x86
rm launcher_arm
