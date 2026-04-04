#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/Thonny.app" >&2
    exit 1
fi

APP_BUNDLE="$1"
NEEDLE="/Library/Frameworks/Python.framework"

if [ ! -d "$APP_BUNDLE" ]; then
    echo "Not a directory: $APP_BUNDLE" >&2
    exit 1
fi

found=0

scan_file() {
    local f="$1"

    # Skip symlinks
    [ -L "$f" ] && return 0

    # Only inspect Mach-O binaries / dylibs / bundles
    if ! file "$f" | grep -q 'Mach-O'; then
        return 0
    fi

    # Check linked libraries
    if otool -L "$f" 2>/dev/null | grep -Fq "$NEEDLE"; then
        echo
        echo "=== LINKS TO $NEEDLE ==="
        echo "$f"
        otool -L "$f" 2>/dev/null | grep -F "$NEEDLE" || true
        found=1
    fi

    # Check rpaths too
    if otool -l "$f" 2>/dev/null | grep -Fq "$NEEDLE"; then
        echo
        echo "=== RPATH/LOAD COMMAND REFERENCES TO $NEEDLE ==="
        echo "$f"
        otool -l "$f" 2>/dev/null | awk -v needle="$NEEDLE" '
            /cmd LC_RPATH/ {in_rpath=1; block=$0 "\n"; next}
            /cmd LC_LOAD_DYLIB/ {in_load=1; block=$0 "\n"; next}
            /cmd LC_LOAD_WEAK_DYLIB/ {in_load=1; block=$0 "\n"; next}
            /cmd LC_REEXPORT_DYLIB/ {in_load=1; block=$0 "\n"; next}
            {
                if (in_rpath || in_load) {
                    block = block $0 "\n"
                    if ($0 ~ needle) {
                        print block
                        print "---"
                        in_rpath=0
                        in_load=0
                        block=""
                    } else if ($1 == "Load" || $1 == "time" || $1 == "path") {
                        # keep going
                    } else if ($1 == "cmdsize") {
                        # still keep going
                    }
                }
            }
        '
        found=1
    fi
}

export NEEDLE
export -f scan_file

while IFS= read -r -d '' file; do
    scan_file "$file"
done < <(find "$APP_BUNDLE" -type f -print0)

if [ "$found" -eq 0 ]; then
    echo "No remaining references to $NEEDLE found in Mach-O files under:"
    echo "  $APP_BUNDLE"
fi
