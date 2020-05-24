#!/usr/bin/env bash
set -e

VERSION=_VERSION_
VARIANT=_VARIANT_

ARCHITECTURE="$(uname -m)"
if [[ "$ARCHITECTURE" != "i686" ]] && [[ "$ARCHITECTURE" != "x86_64" ]]; then
  echo "Thonny only provides pre-built bundles for i686 and x86_64 (not $ARCHITECTURE)"
  exit 1
fi

echo 
echo "This script will download and install Thonny ($VARIANT-$VERSION) for Linux (32 or 64-bit PC)."
read -p "Press ENTER to continue or Ctrl+C to cancel."

FILENAME=$VARIANT-$VERSION-$ARCHITECTURE.tar.gz
URL="https://github.com/thonny/thonny/releases/download/v$VERSION/$FILENAME"

echo "Downloading $URL"

TMPDIR=$(mktemp -d -p .)
wget -O $TMPDIR/$FILENAME $URL
tar -zxf $TMPDIR/$FILENAME -C $TMPDIR
$TMPDIR/thonny/install
rm -rf $TMPDIR

echo 
read -p "Press ENTER to exit the installer."
