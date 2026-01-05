#!/usr/bin/env bash

. venv/bin/activate

echo "isorting ..."
isort thonny

echo
echo "blackening ..."
black thonny

#echo
#echo "running mypy ..."
#mypy thonny

echo
#echo "running pylint ..."
#pylint --msg-template='{abspath}:{line},{column:2d}: {msg} ({symbol})' thonny

uv run pyrefly check --relative-to '' | perl -pe 's/^\s*-->\s+(?=\/)//'
