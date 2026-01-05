#!/usr/bin/env bash

uv run pyrefly check --relative-to '' | perl -pe 's/^\s*-->\s+(?=\/)//'
