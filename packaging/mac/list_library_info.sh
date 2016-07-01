#!/bin/bash

find ~/thonny_template_build -name *.dylib -exec otool -L {} \; -exec printf "\n" \;