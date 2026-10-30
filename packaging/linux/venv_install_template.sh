#!/bin/bash -eu
set -e

VERSION=_VERSION_

TARGET=~/apps/thonny
EXE=$TARGET/bin/thonny
if ! PYLOC="$(command -v python3)"; then
  echo "Could not find python3. Install Python 3.10-3.15 and ensure python3 is on PATH." >&2
  exit 1
fi
if ! PYVER="$(python3 -V 2>&1)"; then
  printf 'Could not run python3 (%s):\n%s\n' "$PYLOC" "$PYVER" >&2
  exit 1
fi
GOODVER="Python 3\.(10|11|12|13|14|15)\.*"
if [[ "$PYVER" =~ $GOODVER ]]; then
  echo "This script will install Thonny $VERSION in $TARGET using $PYVER ($PYLOC)."

  # Install non-pip dependencies
  if [[ -f /etc/debian_version ]]; then
    if ! dpkg -s python3-tk > /dev/null 2>&1; then
      echo "Installing 'python3-tk'..."
      sudo apt-get install -y python3-tk
    fi
    if ! dpkg -s python3-venv > /dev/null 2>&1; then
      echo "Installing 'python3-venv'..."
      sudo apt-get install -y python3-venv
    fi
  elif [[ -f /etc/redhat-release ]]; then
    if ! rpm -qa | grep -q '^python3-tkinter'; then
      echo "Installing 'python3-tkinter'..."
      sudo yum install -y python3-tkinter
    fi
  elif [[ -f /etc/SuSE-release ]]; then # TODO: Legacy fallback; prefer /etc/os-release on modern SUSE/openSUSE
    if ! rpm -qa | grep -q '^python3-tkinter'; then
      echo "Installing 'python3-tkinter'..."
      sudo zypper install -y python3-tkinter
    fi
  elif [[ -f /etc/arch-release ]]; then
    if ! pacman -Qi tk > /dev/null 2>&1; then
      echo "Installing 'tk'..."
      sudo pacman -S --noconfirm tk
    fi
  else
    echo "Unrecognized Linux distribution; continuing without installing system dependencies."
  fi

  if [[ -d "$TARGET" ]]; then
    echo "Removing existing Thonny installation at $TARGET"
    rm -rf "$TARGET"
  fi

  echo "Creating a virtual environment for Thonny"
  python3 -m venv "$TARGET"

  echo ";Existence of this file indicates that Python in this directory is private for Thonny" > "${TARGET}/bin/thonny_python.ini"

  echo "Installing Thonny's extra dependencies"
  "$TARGET/bin/python3" -m pip install _DEPS_
  echo "Installing Thonny and its core dependencies"
  "$TARGET/bin/python3" -m pip install "thonny==${VERSION}"

  echo "Creating the launcher"
  mkdir -p ~/.local/share/applications
  LAUNCHER=~/.local/share/applications/Thonny.desktop
  SITE_PACKAGES=$("$TARGET/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
  quote_desktop_exec() {
    local value="$1"
    # Escape the quoted argument, then the desktop entry's string value.
    value=${value//\\/\\\\}
    value=${value//\"/\\\"}
    value=${value//\`/\\\`}
    value=${value//\$/\\\$}
    value=${value//%/%%}
    value=${value//\\/\\\\}
    printf '"%s"' "$value"
  }
  echo "[Desktop Entry]" > "$LAUNCHER"
  echo "Type=Application" >> "$LAUNCHER"
  echo "Name=Thonny" >> "$LAUNCHER"
  echo "GenericName=Python IDE" >> "$LAUNCHER"
  printf 'Exec=%s -m thonny %%F\n' "$(quote_desktop_exec "$TARGET/bin/python")" >> "$LAUNCHER"
  echo "Comment=Python IDE for beginners" >> "$LAUNCHER"
  echo "Icon=$SITE_PACKAGES/thonny/res/thonny.png" >> "$LAUNCHER"
  echo "StartupWMClass=Thonny" >> "$LAUNCHER"
  echo "Terminal=false" >> "$LAUNCHER"
  echo "Categories=Development;IDE;" >> "$LAUNCHER"
  echo "Keywords=programming;education;" >> "$LAUNCHER"
  echo "MimeType=text/x-python;" >> "$LAUNCHER"
  echo "Actions=Edit;" >> "$LAUNCHER"
  echo "" >> "$LAUNCHER"
  echo "[Desktop Action Edit]" >> "$LAUNCHER"
  printf 'Exec=%s %%F\n' "$(quote_desktop_exec "$EXE")" >> "$LAUNCHER"
  echo "Name=Edit with Thonny" >> "$LAUNCHER"

  UNINSTALLER="${TARGET}/bin/uninstall"
  echo "Creating the uninstaller ($UNINSTALLER)"
  echo "#!/usr/bin/env bash" > "$UNINSTALLER"
  echo "rm -rf \"$TARGET\"" >> "$UNINSTALLER"
  echo "rm -f \"$LAUNCHER\"" >> "$UNINSTALLER"
  chmod +x "$UNINSTALLER"

  echo "------------------------------------------------------------------------------------"
  echo "Thonny is now installed in $TARGET."
  echo "Launch Thonny from your application menu, or run:"
  printf '  %q\n' "$EXE"
  echo "To uninstall Thonny, run:"
  printf '  %q\n' "$UNINSTALLER"
else
  printf 'This installer requires Python 3.10-3.15; found: %s\n' "$PYVER" >&2
  exit 1
fi
