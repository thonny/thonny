#!/bin/bash -eu
set -e

VERSION=_VERSION_

TARGET=~/apps/thonny
PYVER="$(python3 -V 2>&1)"
GOODVER="Python 3\.(10|11|12|13|14|15)\.*"
if [[ "$PYVER" =~ $GOODVER ]]; then
  PYLOC="$(command -v python3 2>&1)"
  echo "This script will install Thonny into a venv related to your existing $PYVER ($PYLOC)."

  # Install non-pip dependencies
  if [[ -f /etc/debian_version ]]; then
    if ! dpkg -s python3-tk > /dev/null 2>&1; then
      echo "Going to install 'python3-tk' first"
      sudo apt-get install -y python3-tk
    fi
    if ! dpkg -s python3-venv > /dev/null 2>&1; then
      echo "Going to install 'python3-venv' first"
      sudo apt-get install -y python3-venv
    fi
  elif [[ -f /etc/redhat-release ]]; then
    if ! rpm -qa | grep -q '^python3-tkinter'; then
      echo "Going to install 'python3-tkinter' first"
      sudo yum install -y python3-tkinter
    fi
  elif [[ -f /etc/SuSE-release ]]; then # TODO: Legacy fallback; prefer /etc/os-release on modern SUSE/openSUSE
    if ! rpm -qa | grep -q '^python3-tkinter'; then
      echo "Going to install 'python3-tkinter' first"
      sudo zypper install -y python3-tkinter
    fi
  elif [[ -f /etc/arch-release ]]; then
    if ! pacman -Qi tk > /dev/null 2>&1; then
      echo "Going to install 'tk' first"
      sudo pacman -S --noconfirm tk
    fi
  else
    echo "Can't determine your package manager, assuming Tkinter and venv are present."
  fi

  if [[ -d "$TARGET" ]]; then
    echo "Removing existing Thonny installation at $TARGET"
    rm -rf "$TARGET"
  fi

  echo "Creating virtual environment for Thonny"
  python3 -m venv "$TARGET"

  echo "Marking virtual environment as private to Thonny"
  echo ";Existence of this file indicates that Python in this directory is private for Thonny" > "${TARGET}/bin/thonny_python.ini"

  echo "Installing Thonny's extra dependencies"
  "$TARGET/bin/python3" -m pip install _DEPS_
  echo "Installing Thonny and its core dependencies"
  "$TARGET/bin/python3" -m pip install "thonny==${VERSION}"

  echo "Creating the launcher"
  mkdir -p ~/.local/share/applications
  LAUNCHER=~/.local/share/applications/Thonny.desktop
  SITE_PACKAGES=$("$TARGET/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
  echo "[Desktop Entry]" > "$LAUNCHER"
  echo "Type=Application" >> "$LAUNCHER"
  echo "Name=Thonny" >> "$LAUNCHER"
  echo "GenericName=Python IDE" >> "$LAUNCHER"
  echo "Exec=$TARGET/bin/python -m thonny %F" >> "$LAUNCHER"
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
  echo "Exec=$TARGET/bin/thonny %F" >> "$LAUNCHER"
  echo "Name=Edit with Thonny" >> "$LAUNCHER"

  UNINSTALLER="${TARGET}/bin/uninstall"
  echo "Creating the uninstaller ($UNINSTALLER)"
  echo "#!/usr/bin/env bash" > "$UNINSTALLER"
  echo "rm -rf \"$TARGET\"" >> "$UNINSTALLER"
  echo "rm -f \"$LAUNCHER\"" >> "$UNINSTALLER"
  chmod +x "$UNINSTALLER"
else
  echo "Can't install Thonny, as your system doesn't seem to have suitable Python interpreter."
  exit 1
fi
