# Linux

## Flatpak

### Build

Get the source code.

    git clone https://github.com/thonny/thonny.git
    cd thonny/packaging/linux

Add the Flathub repository.

    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

Install the FreeDesktop SDK and Platform.

    flatpak install --user flathub org.freedesktop.Sdk//20.08 org.freedesktop.Platform//20.08

Install Flatpak Builder.

    sudo apt install flatpak-builder

Build the Flatpak.

    flatpak-builder --user --install --force-clean --repo=repo thonny-flatpak-build-dir org.thonny.Thonny.Devel.yaml

Run the Flatpak.

    flatpak run org.thonny.Thonny.Devel

### Update

The Python dependencies for the Flatpak are generated with the [Flatpak Pip Generator](https://github.com/flatpak/flatpak-builder-tools/tree/master/pip).
This tool produces the output file `python3-modules.json`, which is included in the Flatpak manifest.
In order to update the dependencies, this file should be regenerated.
Follow the instructions here to do so.

Install the Python dependency `requirements-parser`.

    python -m pip install requirements-parser

Clone the [Flatpak Builder Tools](https://github.com/flatpak/flatpak-builder-tools) repository.

    git clone https://github.com/flatpak/flatpak-builder-tools.git

Run the Flatpak Pip Generator script in the `packaging/linux` directory to produce an updated `python3-modules.json` manifest.
The dependencies are taken from the `requirements-regular-bundle.txt` and `requirements-xxl-bundle.txt` files.

    python flatpak-builder-tools/pip/flatpak-pip-generator \
        $(cat ../requirements-regular-bundle.txt) \
        outdated==0.2.0 \
        $(cat ../requirements-xxl-bundle.txt)

This command currently workarounds an issue in the latest version of the `outdated` package, pulled in by the `birdseye` package.
Version 0.2.1 of the `outdated` package doesn't provide a tarball URL, so the above command overrides this dependency to be version 2.0.0.
In the future, this should be fixed upstream and the command shown here updated.
