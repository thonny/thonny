#!/bin/bash

find ~/pythonny -name *.dylib -exec otool -L {} \; -exec printf "\n" \;