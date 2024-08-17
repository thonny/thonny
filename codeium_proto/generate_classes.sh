#!/bin/bash

set -euxo pipefail

cd "$(dirname "$0")"

buf generate . \
  --path exa/language_server_pb/language_server.proto \
  --include-imports
