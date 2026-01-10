#!/usr/bin/env bash

./format-and-check.sh

cd ../minny || exit
./format-and-check.sh
