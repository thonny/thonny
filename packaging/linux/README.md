# Linux

## Release

On Linux, the AppData file, i.e. `org.thonny.Thonny.appdata.xml` for Thonny, contains information presented users in app stores.
This includes information about each release.
Thus, before cutting a release, it's important to add at least the version of the release and the date to the top of the `releases` section of the AppData file.
It's also helpful to add a description of the changes the new release brings with it.
Make sure to validate this file before a release using `appstreamcli validate`.
This can be done as follows.

    sudo apt install appstream
    appstreamcli org.thonny.Thonny.appdata.xml

Flatpak users may find using the dedicated Flatpak more convenient.

    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak install --user flathub org.freedesktop.appstream-glib
    flatpak run org.freedesktop.appstream-glib validate org.thonny.Thonny.appdata.xml

## Flatpak

The instructions here describe how to build and update the development version of the Thonny Flatpak.

### Build

Get the source code.

    git clone https://github.com/thonny/thonny.git
    cd thonny/packaging/linux

Add the Flathub repository.

    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

Install the FreeDesktop SDK and Platform.

    flatpak install --user flathub org.freedesktop.Sdk//20.08

Install Flatpak Builder.

    sudo apt install flatpak-builder

Build the Flatpak.

    flatpak-builder --user --install --force-clean --repo=repo thonny-flatpak-build-dir org.thonny.Thonny.Devel.yaml

Run the Flatpak.

    flatpak run org.thonny.Thonny.Devel

### Update

The Python dependencies for the Flatpak are generated with the help of the [Flatpak Pip Generator](https://github.com/flatpak/flatpak-builder-tools/tree/master/pip).
This tool produces `json` files for Python packages to be included in the Flatpak manifest's `modules` section.
In order to update or add dependencies in the Flatpak, these dependencies can be generated using the following instructions.

First, install the Python dependency `requirements-parser`.

    python3 -m pip install requirements-parser

Clone the [Flatpak Builder Tools](https://github.com/flatpak/flatpak-builder-tools) repository.

    git clone https://github.com/flatpak/flatpak-builder-tools.git

Now run the Flatpak Pip Generator script for the necessary packages.
The necessary packages are listed in the files `packaging/requirements-regular-bundle.txt` and `packaging/requirements-xxl-bundle.txt` in Thonny's repository.
The following command shows how to retrieve packages from Thonny's `requirements.txt` file by producing a `python3-modules.json` file.
I usually convert these to YAML and place them directly in the Flatpak manifest for readability.

    python3 flatpak-builder-tools/pip/flatpak-pip-generator --runtime org.freedesktop.Sdk//20.08 $(cat ../../requirements.txt)

If you have `org.freedesktop.Sdk//20.08` installed in *both* the user and system installations, the Flatpak Pip Generator will choke generating the manifest.
The best option at the moment is to temporarily remove either the user or the system installation until this issue is fixed upstream.

Note that dependencies may have to be manually updated in order for things to work when the application is built within the Flatpak.
Most often, more dependencies just need to be installed by adding entries to the `modules` section to the Flatpak manifest.
