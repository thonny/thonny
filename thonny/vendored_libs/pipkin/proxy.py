"""
MIT License

Copyright (c) 2022 Aivar Annamaa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import copy
import email.parser
import errno
import hashlib
import io
import json
import logging
import os.path
import shlex
import socket
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import threading
import zipfile
from abc import ABC, abstractmethod
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.error import HTTPError
from urllib.request import urlopen

from pkg_resources import safe_name, safe_version

from pipkin.util import (
    create_dist_info_version_name,
    custom_normalize_dist_name,
    parse_dist_file_name,
)

MP_ORG_INDEX_V1 = "https://micropython.org/pi"
MP_ORG_INDEX_V2 = "https://micropython.org/pi/v2"
PYPI_SIMPLE_INDEX = "https://pypi.org/simple"
SERVER_ENCODING = "utf-8"

# https://github.com/adafruit/circuitpython-build-tools/blob/de44a709f6287d2759df14c89707f2d8f5a026f5/circuitpython_build_tools/scripts/build_bundles.py#L42
NORMALIZED_IRRELEVANT_PACKAGE_NAMES = {
    "adafruit_blinka",
    "adafruit_blinka_bleio",
    "adafruit_blinka_displayio",
    "adafruit_blinka_pyportal",
    "adafruit_python_extended_bus",
    "numpy",
    "pillow",
    "pyasin1",
    "pyserial",
    "scipy",
}

# For efficient caching it's better if the proxy always runs at the same port
PREFERRED_PORT = 36628

logger = logging.getLogger(__name__)


def shlex_join(split_command):
    """Return a shell-escaped string from *split_command*."""
    return " ".join(shlex.quote(arg) for arg in split_command)


class SimpleUrlsParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        self._current_tag: str = ""
        self._current_attrs: List[Tuple[str, str]] = []
        self.file_urls: Dict[str, str] = {}
        super().__init__()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        self._current_tag = tag
        self._current_attrs = attrs

    def handle_data(self, data: str) -> None:
        if self._current_tag == "a":
            for att, val in self._current_attrs:
                if att == "href":
                    self.file_urls[data] = val

    def handle_endtag(self, tag):
        pass


class BaseIndexDownloader(ABC):
    def __init__(self, index_url: str):
        self._index_url = index_url.rstrip("/")

    @abstractmethod
    def get_dist_file_names(self, dist_name: str) -> Optional[List[str]]:
        raise NotImplementedError()

    @abstractmethod
    def get_file_content(self, dist_name: str, file_name: str) -> bytes:
        raise NotImplementedError()


class RegularIndexDownloader(BaseIndexDownloader, ABC):
    def __init__(self, index_url: str):
        super().__init__(index_url)
        self._dist_urls_cache: Dict[str, Dict[str, str]] = {}

    def get_dist_file_names(self, dist_name: str) -> Optional[List[str]]:
        urls = self._get_dist_urls(dist_name)
        if urls is None:
            return None
        return list(urls.keys())

    def get_file_content(self, dist_name: str, file_name: str) -> bytes:
        if self._should_return_dummy(dist_name):
            return create_dummy_dist(dist_name, file_name)
        else:
            original_bytes = self._download_file(dist_name, file_name)
            return self._tweak_file(dist_name, file_name, original_bytes)

    def _get_dist_urls(self, dist_name: str) -> Optional[Dict[str, str]]:
        """
        Returns file names and url-s for constructing the dist index page.
        """
        if dist_name not in self._dist_urls_cache:
            self._dist_urls_cache[dist_name] = self._download_file_urls(dist_name)

        return self._dist_urls_cache[dist_name]

    @abstractmethod
    def _download_file_urls(self, dist_name) -> Optional[Dict[str, str]]:
        raise NotImplementedError()

    def _download_file(self, dist_name: str, file_name: str) -> bytes:
        urls = self._get_dist_urls(dist_name)
        assert urls

        assert file_name in urls
        url = urls[file_name]

        logger.debug("Downloading file from %s", url)
        with urlopen(url) as result:
            logger.debug("Headers: %r", result.headers.items())
            return result.read()

    def _tweak_file(self, dist_name: str, file_name: str, original_bytes: bytes) -> bytes:
        if not file_name.lower().endswith(".tar.gz"):
            return original_bytes

        # In case of upip packages (tar.gz-s without setup.py) reverse following process:
        # https://github.com/micropython/micropython-lib/commit/3a6ab0b

        in_tar = tarfile.open(fileobj=io.BytesIO(original_bytes), mode="r:gz")
        out_buffer = io.BytesIO()
        out_tar = tarfile.open(fileobj=out_buffer, mode="w:gz")

        wrapper_dir = None
        py_modules = []
        packages = []
        metadata_bytes = None
        requirements = []
        egg_info_path = None

        for info in in_tar:
            logger.debug("Processing %r (name:%r, isfile:%r)", info, info.name, info.isfile())
            out_info = copy.copy(info)

            if info.isdir():
                content = None
            else:
                with in_tar.extractfile(info) as f:
                    content = f.read()

            if "/" in info.name:
                wrapper_dir, rel_name = info.name.split("/", maxsplit=1)
            else:
                assert info.isdir()
                wrapper_dir, rel_name = info.name, ""

            assert custom_normalize_dist_name(wrapper_dir).startswith(
                custom_normalize_dist_name(dist_name)
            )

            rel_name = rel_name.strip("/")
            rel_segments = rel_name.split("/")

            # collect information about the original tar
            if rel_name == "setup.py":
                logger.debug("The archive contains setup.py. No tweaks needed")
                return original_bytes
            elif ".egg-info" in rel_name:
                if rel_name.endswith(".egg-info/PKG-INFO"):
                    egg_info_path = rel_name[: -len("/PKG-INFO")]
                    metadata_bytes = content
                elif rel_name.endswith(".egg-info/requires.txt"):
                    requirements = content.decode("utf-8").strip().splitlines()
            elif len(rel_segments) == 1:
                # toplevel item outside of egg-info
                if info.isfile() and rel_name.endswith(".py"):
                    # toplevel module
                    module_name = rel_name[: -len(".py")]
                    py_modules.append(module_name)
                else:
                    if info.isdir():
                        # Assuming all toplevel directories represent packages.
                        packages.append(rel_name)
            else:
                # Assuming an item inside a subdirectory.
                # If it's a py, it will be included together with containing package,
                # otherwise it will be picked up by package_data wildcard expression.
                if rel_segments[0] not in packages:
                    # directories may not have their own entry
                    packages.append(rel_segments[0])

            # all existing files and dirs need to be added without changing
            out_tar.addfile(out_info, io.BytesIO(content))

        assert wrapper_dir
        assert metadata_bytes

        logger.debug("%s is optimized for upip. Re-constructing missing files", file_name)
        logger.debug("py_modules: %r", py_modules)
        logger.debug("packages: %r", packages)
        logger.debug("requirements: %r", requirements)
        metadata = self._parse_metadata(metadata_bytes)
        logger.debug("metadata: %r", metadata)
        setup_py = self._create_setup_py(metadata, py_modules, packages, requirements)
        logger.debug("setup.py: %s", setup_py)

        self._add_file_to_tar(wrapper_dir + "/setup.py", setup_py.encode("utf-8"), out_tar)
        self._add_file_to_tar(wrapper_dir + "/PKG-INFO", metadata_bytes, out_tar)
        self._add_file_to_tar(
            wrapper_dir + "/setup.cfg",
            b"""[egg_info]
tag_build = 
tag_date = 0
""",
            out_tar,
        )
        self._add_file_to_tar(
            wrapper_dir + "/" + egg_info_path + "/dependency_links.txt", b"\n", out_tar
        )
        self._add_file_to_tar(
            wrapper_dir + "/" + egg_info_path + "/top_level.txt",
            ("\n".join(packages + py_modules) + "\n").encode("utf-8"),
            out_tar,
        )

        # TODO: recreate SOURCES.txt and test with data files

        out_tar.close()

        out_bytes = out_buffer.getvalue()

        # with open("_temp.tar.gz", "wb") as fp:
        #    fp.write(out_bytes)

        return out_bytes

    def _add_file_to_tar(self, name: str, content: bytes, tar: tarfile.TarFile) -> None:
        stream = io.BytesIO(content)
        info = tarfile.TarInfo(name=name)
        info.size = len(content)
        tar.addfile(info, stream)

    def _should_return_dummy(self, dist_name: str) -> bool:
        return custom_normalize_dist_name(
            dist_name
        ) in NORMALIZED_IRRELEVANT_PACKAGE_NAMES or custom_normalize_dist_name(
            dist_name
        ).startswith(
            "adafruit_blinka_"
        )

    def _parse_metadata(self, metadata_bytes) -> Dict[str, str]:
        metadata = email.parser.Parser().parsestr(metadata_bytes.decode("utf-8"))
        return {
            key: metadata.get(key)
            for key in (
                "Metadata-Version",
                "Name",
                "Version",
                "Summary",
                "Home-page",
                "Author",
                "Author-email",
                "License",
            )
        }

    def _create_setup_py(
        self,
        metadata: Dict[str, str],
        py_modules: List[str],
        packages: List[str],
        requirements: List[str],
    ) -> str:
        src = dedent(
            """
            from setuptools import setup
            setup (
            """
        ).lstrip()

        for src_key, target_key in [
            ("Name", "name"),
            ("Version", "version"),
            ("Summary", "description"),
            ("Home-page", "url"),
            ("Author", "author"),
            ("Author-email", "author_email"),
            ("License", "license"),
        ]:
            if src_key in metadata:
                src += f"    {target_key}={metadata[src_key]!r},\n"

        if requirements:
            src += f"    install_requires={requirements!r},\n"

        if py_modules:
            src += f"    py_modules={py_modules!r},\n"

        if packages:
            src += f"    packages={packages!r},\n"

        # include all other files as package data
        src += "    package_data={'*': ['*', '*/*', '*/*/*', '*/*/*/*', '*/*/*/*/*', '*/*/*/*/*/*', '*/*/*/*/*/*/*', '*/*/*/*/*/*/*/*']}\n"

        src += ")\n"
        return src


class SimpleIndexDownloader(RegularIndexDownloader):
    def _download_file_urls(self, dist_name) -> Optional[Dict[str, str]]:
        url = f"{self._index_url}/{dist_name}"
        logger.info("Downloading file urls from simple index %s", url)

        try:
            with urlopen(url) as fp:
                parser = SimpleUrlsParser()
                parser.feed(fp.read().decode("utf-8"))
                return parser.file_urls
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                raise e


class JsonIndexDownloader(RegularIndexDownloader):
    def _download_file_urls(self, dist_name) -> Optional[Dict[str, str]]:
        metadata_url = f"{self._index_url}/{dist_name}/json"
        logger.info("Downloading file urls from json index at %s", metadata_url)

        result = {}
        try:
            with urlopen(metadata_url) as fp:
                data = json.load(fp)
                releases = data["releases"]
                for ver in releases:
                    for file in releases[ver]:
                        file_url = file["url"]
                        if "filename" in file:
                            file_name = file["filename"]
                        else:
                            # micropython.org/pi doesn't have it
                            file_name = file_url.split("/")[-1]
                            # may be missing micropython prefix
                            if not file_name.startswith(dist_name):
                                # Let's hope version part doesn't contain dashes
                                _, suffix = file_name.split("-")
                                file_name = dist_name + "-" + suffix
                        result[file_name] = file_url
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                raise e
        return result


class MpOrgV1IndexDownloader(JsonIndexDownloader):
    def _download_file_urls(self, dist_name) -> Optional[Dict[str, str]]:
        if not custom_normalize_dist_name(dist_name).startswith("micropython_"):
            return None

        return super()._download_file_urls(dist_name)


class MpOrgV2IndexDownloader(BaseIndexDownloader):
    def __init__(self, index_url):
        self._packages = None
        super().__init__(index_url)

    def get_dist_file_names(self, dist_name: str) -> Optional[List[str]]:
        # there is no per-package, all-versions metadata resource. Need to use the global index
        meta = self._get_dist_metadata(dist_name)
        if meta is None:
            return None

        # Collect relationship between version and constructed file names so that I won't need to parse file name later.
        meta["original_versions_per_file_name"] = {}

        result = []
        for version in meta["versions"]["py"]:
            file_name = create_dist_info_version_name(dist_name, version) + "-py3-none-any.whl"
            meta["original_versions_per_file_name"][file_name] = version
            result.append(file_name)

        return result

    def get_file_content(self, dist_name: str, file_name: str) -> bytes:
        dist_meta = self._get_dist_metadata(dist_name)
        original_name = dist_meta["name"]

        original_versions = dist_meta.get("original_versions_per_file_name", None)
        assert isinstance(original_versions, dict)
        original_version = original_versions.get(file_name, None)
        assert isinstance(original_version, str)

        version_meta_url = f"{self._index_url}/package/py/{original_name}/{original_version}.json"
        with urlopen(version_meta_url) as fp:
            version_meta = json.load(fp)

        return self._construct_wheel_content(dist_meta, version_meta)

    def _construct_wheel_content(
        self, dist_meta: Dict[str, Any], version_meta: Dict[str, Any]
    ) -> bytes:
        urls_per_wheel_path = {}

        for wheel_path, short_hash in version_meta.get("hashes", []):
            urls_per_wheel_path[
                wheel_path
            ] = f"{self._index_url}/file/{short_hash[:2]}/{short_hash}"

        for wheel_path, url in version_meta.get("urls", []):
            urls_per_wheel_path[wheel_path] = url

        bytes_per_wheel_path = {}
        for wheel_path, url in urls_per_wheel_path.items():
            with urlopen(url) as fp:
                bytes_per_wheel_path[wheel_path] = fp.read()

        # construct metadata files
        meta_dir_prefix = create_dist_info_version_name(dist_meta["name"], version_meta["version"])
        meta_dir = f"{meta_dir_prefix}.dist-info"
        summary = dist_meta.get("description", "").replace("\r\n", "\n").replace("\n", " ")

        metadata = textwrap.dedent(
            f"""
            Metadata-Version: 2.1
            Name: {safe_name(dist_meta["name"])}
            Version: {safe_version(version_meta["version"])}
            Summary: {summary}
            Author: {dist_meta.get("author", "")}
            License: {dist_meta.get("license", "")}
            """
        ).lstrip()

        for dep_name, dep_version in version_meta.get("deps", []):
            metadata += f"Requires-Dist: {dep_name}"
            if dep_version and dep_version != "latest":
                metadata += " ("
                if dep_version[0] not in "<>=":
                    metadata += "=="
                metadata += dep_version
                metadata += ")"
            metadata += "\n"

        bytes_per_wheel_path[f"{meta_dir}/METADATA"] = metadata.encode("utf-8")

        bytes_per_wheel_path[f"{meta_dir}/WHEEL"] = (
            textwrap.dedent(
                """
            Wheel-Version: 1.0
            Generator: bdist_wheel (0.37.1)
            Root-Is-Purelib: true
            Tag: py3-none-any
            """
            )
            .lstrip()
            .encode("utf-8")
        )

        record_lines = []
        for wheel_path, content in bytes_per_wheel_path.items():
            digest = hashlib.sha256(content).hexdigest()
            record_lines.append(f"{wheel_path},sha256={digest},{len(content)}")
        record_lines.append(f"{meta_dir}/RECORD,,")

        bytes_per_wheel_path[f"{meta_dir}/RECORD"] = ("\n".join(record_lines) + "\n").encode(
            "utf-8"
        )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, mode="a", compression=zipfile.ZIP_DEFLATED, allowZip64=False
        ) as fp:
            for wheel_path, content in bytes_per_wheel_path.items():
                fp.writestr(wheel_path, content)

        with open(os.path.expanduser("~/out.whl"), "wb") as fp:
            fp.write(zip_buffer.getvalue())
        return zip_buffer.getvalue()

    def _get_dist_metadata(self, dist_name: str) -> Optional[Dict[Any, Any]]:
        if self._packages is None:
            with urlopen(MP_ORG_INDEX_V2 + "/index.json") as fp:
                self._packages = json.load(fp)["packages"]

        for package in self._packages:
            if custom_normalize_dist_name(package["name"]) == custom_normalize_dist_name(dist_name):
                return package

        return None


class PipkinProxy(HTTPServer):
    def __init__(
        self, no_mp_org: bool, index_url: Optional[str], extra_index_urls: List[str], port: int
    ):
        self._downloaders: List[BaseIndexDownloader] = []
        self._downloaders_by_dist_name: Dict[str, Optional[BaseIndexDownloader]] = {}
        if not no_mp_org:
            # V1 first, because it only considers packages with "micropython-"-prefix
            self._downloaders.append(MpOrgV1IndexDownloader(MP_ORG_INDEX_V1))
            self._downloaders.append(MpOrgV2IndexDownloader(MP_ORG_INDEX_V2))
        self._downloaders.append(SimpleIndexDownloader(index_url or PYPI_SIMPLE_INDEX))
        for url in extra_index_urls:
            self._downloaders.append(SimpleIndexDownloader(url))
        super().__init__(("127.0.0.1", port), PipkinProxyHandler)

    def get_downloader_for_dist(self, dist_name: str) -> Optional[BaseIndexDownloader]:
        if dist_name not in self._downloaders_by_dist_name:
            for downloader in self._downloaders:
                logger.debug("Checking if %s has %r", downloader, dist_name)
                file_names = downloader.get_dist_file_names(dist_name)
                if file_names is not None:
                    logger.debug("Got %r file names", len(file_names))
                    self._downloaders_by_dist_name[dist_name] = downloader
                    break
                else:
                    logger.debug("Got None. Trying next downloader")
            else:
                self._downloaders_by_dist_name[dist_name] = None

        return self._downloaders_by_dist_name[dist_name]

    def get_index_url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class PipkinProxyHandler(BaseHTTPRequestHandler):
    def __init__(
        self,
        request: Union[socket.socket, Tuple[bytes, socket.socket]],
        client_address: Tuple[str, int],
        server: BaseServer,
    ):
        logger.debug("Creating new handler")
        assert isinstance(server, PipkinProxy)
        self.proxy: PipkinProxy = server
        super().__init__(request, client_address, server)

    def do_GET(self) -> None:
        path = self.path.strip("/")
        logger.debug("do_GET for %s", path)
        if "/" in path:
            assert path.count("/") == 1
            self._serve_file(*path.split("/"))
        else:
            self._serve_distribution_page(path)

    def _serve_distribution_page(self, dist_name: str) -> None:
        logger.debug("Serving index page for %s", dist_name)
        downloader = self.proxy.get_downloader_for_dist(dist_name)
        if downloader is None:
            self.send_response(404)
            self.end_headers()
            return

        # TODO: check https://discuss.python.org/t/community-testing-of-packaging-tools-against-non-warehouse-indexes/13442

        file_names = downloader.get_dist_file_names(dist_name)
        # logger.debug("File urls: %r", file_names)
        self.send_response(200)
        self.send_header("Content-type", f"text/html; charset={SERVER_ENCODING}")
        self.send_header("Cache-Control", "max-age=600, public")
        self.end_headers()
        self.wfile.write("<!DOCTYPE html><html><body>\n".encode(SERVER_ENCODING))
        for file_name in file_names:
            self.wfile.write(
                f"<a href='/{dist_name}/{file_name}/'>{file_name}</a>\n".encode(SERVER_ENCODING)
            )
        self.wfile.write("</body></html>".encode(SERVER_ENCODING))

    def _serve_file(self, dist_name: str, file_name: str):
        logger.debug("Serving %s for %s", file_name, dist_name)

        downloader = self.proxy.get_downloader_for_dist(dist_name)
        assert downloader is not None
        file_content = downloader.get_file_content(dist_name, file_name)

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Cache-Control", "max-age=365000000, immutable, public")
        self.end_headers()

        block_size = 4096
        for start_index in range(0, len(file_content), block_size):
            block = file_content[start_index : start_index + block_size]
            self.wfile.write(block)


def start_proxy(
    no_mp_org: bool,
    index_url: Optional[str],
    extra_index_urls: List[str],
) -> PipkinProxy:
    port = PREFERRED_PORT
    if no_mp_org:
        # Use different port for different set of source indexes, otherwise
        # pip may use wrong cached wheel.
        port += 7
    try:
        proxy = PipkinProxy(no_mp_org, index_url, extra_index_urls, port)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.warning("Port %s was in use. Letting OS choose.", port)
            proxy = PipkinProxy(no_mp_org, index_url, extra_index_urls, 0)
        else:
            raise e

    server_thread = threading.Thread(target=proxy.serve_forever)
    server_thread.start()

    return proxy


def create_dummy_dist(dist_name: str, file_name: str) -> bytes:
    logger.info("Creating dummy content for %s", file_name)
    parsed_dist_name, version, suffix = parse_dist_file_name(file_name)
    assert custom_normalize_dist_name(dist_name) == custom_normalize_dist_name(parsed_dist_name)

    with tempfile.TemporaryDirectory(prefix="pipkin-proxy") as tmp:
        setup_py_path = os.path.join(tmp, "setup.py")
        with open(setup_py_path, "w", encoding="utf-8") as fp:
            fp.write(
                dedent(
                    f"""
            from setuptools import setup
            setup(
                name={dist_name!r},
                version={version!r},
                description="Dummy package for satisfying formal requirements",
                long_description="?",
                url="?",
                author="?"
            )
            """
                )
            )

        if suffix == ".whl":
            setup_py_args = ["bdist_wheel"]
        elif suffix == ".zip":
            setup_py_args = ["sdist", "--formats=zip"]
        elif suffix == ".tar.gz":
            setup_py_args = ["sdist", "--formats=gztar"]
        else:
            raise AssertionError("Unexpected suffix " + suffix)

        args = [sys.executable, setup_py_path] + setup_py_args
        subprocess.check_call(args, executable=args[0], cwd=tmp, stdin=subprocess.DEVNULL)

        dist_dir = os.path.join(tmp, "dist")
        dist_files = os.listdir(dist_dir)

        assert len(dist_files) == 1
        with open(os.path.join(dist_dir, dist_files[0]), "rb") as bfp:
            return bfp.read()
