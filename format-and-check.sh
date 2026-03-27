#!/usr/bin/env bash

echo "# isort #######################################"
uv run isort src tests

echo "# format #################################"
uv run black thonny

