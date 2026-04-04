#!/usr/bin/env bash

SITEPKG="./build"

find "$SITEPKG" \( -name '*.so' -o -name '*.dylib' \) -print0 |
while IFS= read -r -d '' f; do
  info="$(lipo -info "$f" 2>/dev/null || true)"
  case "$info" in
    *"Non-fat file:"*)
      echo "NON-UNIVERSAL: $f :: $info"
      ;;
    *"Architectures in the fat file:"*)
      # universal/fat; keep only ones missing either arm64 or x86_64
      echo "$info" | grep -q 'arm64' || echo "MISSING arm64:  $f :: $info"
      echo "$info" | grep -q 'x86_64' || echo "MISSING x86_64: $f :: $info"
      ;;
    *)
      # not a Mach-O binary or lipo couldn't parse it
      :
      ;;
  esac
done
