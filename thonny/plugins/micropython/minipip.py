#!/usr/bin/env python3

import io
import json
import os.path
import sys
import shlex
import shutil
import subprocess
import tarfile
import tempfile
import textwrap
from typing import Union, List, Dict, Any, Optional, Tuple
from urllib.error import HTTPError
from urllib.request import urlopen
import pkg_resources
import logging

from pkg_resources import Requirement

logger = logging.getLogger(__name__)

MP_ORG_INDEX = "https://micropython.org/pi"
PYPI_INDEX = "https://pypi.org/pypi"
DEFAULT_INDEX_URLS = [MP_ORG_INDEX, PYPI_INDEX]

__version__ = "0.1b1"


class UserError(RuntimeError):
    pass


class NotUpipCompatible(RuntimeError):
    pass


def install(
    spec: Union[List[str], str],
    target_dir: str,
    index_urls: List[str] = None,
    port: Optional[str] = None,
):
    if not index_urls:
        index_urls = DEFAULT_INDEX_URLS

    temp_dir = tempfile.mkdtemp()
    try:
        _install_to_local_temp_dir(spec, temp_dir, index_urls)
        if port is not None:
            _copy_to_micropython_over_serial(temp_dir, port, target_dir)
        else:
            _copy_to_local_target_dir(temp_dir, target_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _copy_to_local_target_dir(source_dir: str, target_dir: str):
    logger.info("Copying files to %s", os.path.abspath(target_dir))
    # Copying manually in order to be able to use os.fsync
    # see https://learn.adafruit.com/adafruit-circuit-playground-express/creating-and-editing-code#1-use-an-editor-that-writes-out-the-file-completely-when-you-save-it
    for root, dirs, files in os.walk(source_dir):
        relative_dir = root[len(source_dir) :].lstrip("/\\")
        full_target_dir = os.path.join(target_dir, relative_dir)
        for dir_name in dirs:
            full_path = os.path.join(full_target_dir, dir_name)
            if os.path.isdir(full_path):
                logger.info("Directory %s already exists", os.path.join(relative_dir, dir_name))
            elif os.path.isfile(full_path):
                raise UserError("Can't treat existing file %s as directory", full_path)
            else:
                logger.info("Creating %s", os.path.join(relative_dir, dir_name))
                os.makedirs(full_path, 0o700)

        for file_name in files:
            full_source_path = os.path.join(root, file_name)
            full_target_path = os.path.join(full_target_dir, file_name)
            logger.debug("Preparing %s => %s", full_source_path, full_target_path)

            if os.path.isfile(full_target_path):
                logger.info("Overwriting %s", os.path.join(relative_dir, file_name))
            elif os.path.isdir(full_target_path):
                raise UserError("Can't treat existing directory %s as file", full_target_path)
            else:
                logger.info("Copying %s", os.path.join(relative_dir, file_name))

            with open(full_source_path, "rb") as in_fp, open(full_target_path, "wb") as out_fp:
                out_fp.write(in_fp.read())
                out_fp.flush()
                os.fsync(out_fp)


def _copy_to_micropython_over_serial(source_dir: str, port: str, target_dir: str):
    assert target_dir.startswith("/")

    cmd = _get_rshell_command() + ["-p", port, "rsync", source_dir, "/pyboard" + target_dir]
    logger.debug("Uploading with rsync: %s", shlex.join(cmd))
    subprocess.check_call(cmd)


def _get_rshell_command() -> Optional[List[str]]:
    if shutil.which("rshell"):
        return ["rshell"]
    else:
        return None


def _install_to_local_temp_dir(
    spec: Union[List[str], str], temp_install_dir: str, index_urls: List[str]
) -> None:
    if isinstance(spec, str):
        specs = [spec]
    else:
        specs = spec

    pip_specs = _install_all_upip_compatible(specs, temp_install_dir, index_urls)

    if pip_specs:
        _install_with_pip(pip_specs, temp_install_dir, index_urls)


def _install_all_upip_compatible(
    specs: List[str], install_dir: str, index_urls: List[str]
) -> List[str]:
    """Returns list of specs which must be installed with pip"""
    installed_specs = set()
    specs_to_be_processed = specs.copy()
    pip_specs = []

    while specs_to_be_processed:
        spec = specs_to_be_processed.pop(0)
        if spec in installed_specs or spec in pip_specs:
            continue

        req = pkg_resources.Requirement.parse(spec)

        logger.info("Processing '%s'", req)
        meta, version = _fetch_metadata_and_resolve_version(req, index_urls)
        logger.info("Inspecting version %s", version)
        assets = meta["releases"][version]

        if len(assets) != 1 or not assets[0]["url"].endswith(".tar.gz"):
            logger.info(
                "'%s' will be installed with pip (not having single tar.gz asset).",
                req.project_name,
            )
            pip_specs.append(spec)
            continue

        try:
            dep_specs = _install_single_upip_compatible_from_url(
                req.project_name, assets[0]["url"], install_dir
            )
            installed_specs.add(spec)
            if dep_specs:
                logger.info("Dependencies of '%s': %s", spec, dep_specs)
                for dep_spec in dep_specs:
                    if dep_spec not in installed_specs and dep_spec not in specs_to_be_processed:
                        specs_to_be_processed.append(dep_spec)
        except NotUpipCompatible:
            pip_specs.append(spec)

    return pip_specs


def _install_single_upip_compatible_from_url(
    project_name: str, url: str, target_dir: str
) -> List[str]:
    with urlopen(url) as fp:
        download_data = fp.read()

    tar = tarfile.open(fileobj=io.BytesIO(download_data), mode="r:gz")

    deps = []

    content: Dict[str, Optional[bytes]] = {}

    for info in tar:
        if "/" in info.name:
            dist_name, rel_name = info.name.split("/", maxsplit=1)
        else:
            dist_name, rel_name = info.name, ""

        if rel_name == "setup.py":
            logger.debug("The archive contains setup.py. The package will be installed with pip")
            raise NotUpipCompatible()

        if ".egg-info/PKG-INFO" in rel_name:
            continue

        if ".egg-info/requires.txt" in rel_name:
            for line in tar.extractfile(info):
                line = line.strip()
                if line and not line.startswith(b"#"):
                    deps.append(line.decode())
            continue

        if ".egg-info" in rel_name:
            continue

        if info.isdir():
            content[os.path.join(target_dir, rel_name)] = None
        elif info.isfile():
            content[os.path.join(target_dir, rel_name)] = tar.extractfile(info).read()

    # write files only after the package is fully inspected and found to be upip compatible
    logger.info("Extracting '%s' from %s to %s", project_name, url, os.path.abspath(target_dir))
    for path in content:
        data = content[path]
        if data is None:
            os.makedirs(path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fp:
                fp.write(data)

    return deps


def _install_with_pip(specs: List[str], target_dir: str, index_urls: List[str]):
    logger.info("Installing with pip: %s", specs)

    suitable_indexes = [url for url in index_urls if url != MP_ORG_INDEX]
    if not suitable_indexes:
        raise UserError("No suitable indexes for pip")

    index_args = ["--index-url", suitable_indexes.pop(0)]
    while suitable_indexes:
        index_args += ["--extra-index-url", suitable_indexes.pop(0)]
    if index_args == ["--index-url", "https://pypi.org/pypi"]:
        # for some reason, this form does not work for some versions of some packages
        # (eg. micropython-os below 0.4.4)
        index_args = []

    args = [
        "--no-input",
        "--disable-pip-version-check",
        "install",
        "--upgrade",
        "--target",
        target_dir,
    ] + index_args

    pip_cmd = (
        [
            sys.executable,
            "-m",
            "pip",
        ]
        + args
        + specs
    )
    logger.debug("Calling pip: %s", shlex.join(pip_cmd))
    subprocess.check_call(pip_cmd)

    # delete files not required for MicroPython
    for root, dirs, files in os.walk(target_dir):
        for dir_name in dirs:
            if dir_name.endswith(".dist-info") or dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))

        for file_name in files:
            if file_name.endswith(".pyc"):
                os.remove(os.path.join(root, file_name))


def _fetch_metadata_and_resolve_version(
    req: Requirement, index_urls: List[str]
) -> Tuple[Dict[str, Any], str]:

    ver_specs = req.specs

    for i, index_url in enumerate(index_urls):
        try:
            url = "%s/%s/json" % (index_url, req.project_name)
            logger.info("Querying package metadata from %s", url)
            with urlopen(url) as fp:
                meta = json.load(fp)
            current_version = meta["info"]["version"]

            if not ver_specs:
                return meta, current_version

            ver = _resolve_version(req, meta)
            if ver is None:
                logger.info("Could not find suitable version from %s", index_url)
                continue

            return meta, ver
        except HTTPError as e:
            if e.code == 404:
                logger.info("Could not find '%s' from %s", req.project_name, index_url)
            else:
                raise

    raise UserError(
        "Could not find '%s' from any of the indexes %s" % (req.project_name, index_urls)
    )


def _read_requirements(req_file: str) -> List[str]:
    if not os.path.isfile(req_file):
        raise UserError("Can't find '%s'" % req_file)

    result = []
    with open(req_file, "r", errors="replace") as fp:
        for line in fp:
            line = line.strip()
            if line and not line.startswith("#"):
                result.append(line)

    return result


def _resolve_version(req: Requirement, main_meta: Dict[str, Any]) -> Optional[str]:
    matching_versions = []
    for ver in main_meta["releases"]:
        if ver in req and len(main_meta["releases"][ver]) > 0:
            matching_versions.append(ver)

    if not matching_versions:
        return None

    return sorted(matching_versions, key=pkg_resources.parse_version)[-1]


def main(raw_args: Optional[List[str]] = None) -> int:
    if raw_args is None:
        raw_args = sys.argv[1:]

    import argparse

    description = textwrap.dedent(
        """
        Meant for installing both upip and pip compatible distribution packages from 
        PyPI and micropython.org/pi to a local directory, USB volume or directly to 
        MicroPython filesystem over serial connection (requires rshell).    
    """
    ).strip()

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "command", help="Currently the only supported command is 'install'", choices=["install"]
    )
    parser.add_argument(
        "specs",
        help="Package specification, eg. 'micropython-os' or 'micropython-os>=0.6'",
        nargs="+",
        metavar="package_spec",
    )
    parser.add_argument(
        "-r",
        "--requirement",
        help="Install from the given requirements file.",
        nargs="*",
        dest="requirement_files",
        metavar="REQUIREMENT_FILE",
        default=[],
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Serial port of the device",
        nargs="?",
    )
    parser.add_argument(
        "-t",
        "--target",
        help="Target directory (on device, if port is given, otherwise local)",
        default=".",
        dest="target_dir",
        metavar="TARGET_DIR",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--index-url",
        help="Custom index URL",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show more details about the process",
        action="store_true",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Don't show non-error output",
        action="store_true",
    )
    parser.add_argument(
        "--version",
        help="Show program version and exit",
        action="store_true",
    )
    args = parser.parse_args(args=raw_args)

    all_specs = args.specs
    for req_file in args.requirement_files:
        all_specs.extend(_read_requirements(req_file))

    if args.index_url:
        index_urls = [args.index_url]
    else:
        index_urls = DEFAULT_INDEX_URLS

    if args.quiet and args.verbose:
        print("Can't be quiet and verbose at the same time", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        logging_level = logging.DEBUG
    elif args.quiet:
        logging_level = logging.ERROR
    else:
        logging_level = logging.INFO

    logger.setLevel(logging_level)
    logger.propagate = True
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging_level)
    logger.addHandler(console_handler)

    if args.port and not _get_rshell_command():
        print(
            "Could not find rshell (required for uploading when serial port is given)",
            file=sys.stderr,
        )
        return 1

    if args.port and not args.target_dir.startswith("/"):
        print("If port is given then target dir must be absolute Unix-style path")
        return 1

    if args.version:
        print(__version__)
        return 0

    try:
        install(all_specs, target_dir=args.target_dir, index_urls=index_urls, port=args.port)
    except UserError as e:
        print("ERROR:", e, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        # assuming the subprocess (pip or rshell) already printed the error
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
