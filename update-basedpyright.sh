#!/usr/bin/env bash

TARGET=thonny/vendored_libs

rm -rf $TARGET/basedpyright
pip3 install --upgrade --no-dependencies --target $TARGET basedpyright

rm -rf $TARGET/basedpyright*.dist-info
rm -rf ${TARGET:?}/bin
rm -rf $TARGET/basedpyright/dist/typeshed-fallback/stubs/*
rm $TARGET/basedpyright/__init__.py
rm $TARGET/basedpyright/__main__.py
rm $TARGET/basedpyright/index.js
rm $TARGET/basedpyright/pyright.py
rm $TARGET/basedpyright/dist/pyright.js
rm $TARGET/basedpyright/dist/pyright.js
rm $TARGET/basedpyright/dist/pyright.js.map
rm $TARGET/basedpyright/dist/pyright-langserver.js.map
