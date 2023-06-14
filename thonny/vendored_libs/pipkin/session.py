import hashlib
import json
import os.path
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from logging import getLogger
from typing import Dict, List, Optional, Set, Tuple
from urllib.request import urlopen

import filelock
from filelock import BaseFileLock, FileLock

from pipkin.adapters import Adapter
from pipkin.common import UserError
from pipkin.proxy import start_proxy
from pipkin.util import (
    get_base_executable,
    get_user_cache_dir,
    get_venv_executable,
    get_venv_site_packages_path,
    parse_meta_dir_name,
)

logger = getLogger(__name__)

INITIAL_VENV_DISTS = ["pip", "setuptools", "pkg_resources", "wheel"]
INITIAL_VENV_FILES = ["easy_install.py"]
META_ENCODING = "utf-8"


@dataclass(frozen=True)
class DistInfo:
    key: str
    project_name: str
    version: str
    location: str


class Session:
    """
    Allows performing several commands in row without releasing the venv.
    """

    def __init__(self, adapter: Adapter, tty: bool = True):
        self._adapter = adapter
        self._venv_lock: Optional[BaseFileLock] = None
        self._venv_dir: Optional[str] = None
        self._quiet = False
        self._tty = tty

    def install(
        self,
        specs: Optional[List[str]] = None,
        requirement_files: Optional[List[str]] = None,
        constraint_files: Optional[List[str]] = None,
        pre: bool = False,
        no_deps: bool = False,
        no_mp_org: bool = False,
        index_url: Optional[str] = None,
        extra_index_urls: Optional[List[str]] = None,
        no_index: bool = False,
        find_links: Optional[str] = None,
        target: Optional[str] = None,
        user: bool = False,
        upgrade: bool = False,
        upgrade_strategy: str = "only-if-needed",
        force_reinstall: bool = False,
        compile: Optional[bool] = None,
        mpy_cross: Optional[str] = None,
        **_,
    ):
        logger.debug("Starting install")

        if compile is None and mpy_cross:
            compile = True

        args = ["install", "--no-compile", "--use-pep517"]

        if upgrade:
            args.append("--upgrade")
        if upgrade_strategy:
            args += ["--upgrade-strategy", upgrade_strategy]
        if force_reinstall:
            args.append("--force-reinstall")

        args += self._format_selection_args(
            specs=specs,
            requirement_files=requirement_files,
            constraint_files=constraint_files,
            pre=pre,
            no_deps=no_deps,
        )

        self._populate_venv()
        state_before = self._get_venv_state()
        self._invoke_pip_with_index_args(
            args,
            no_mp_org=no_mp_org,
            index_url=index_url,
            extra_index_urls=extra_index_urls or [],
            no_index=no_index,
            find_links=find_links,
        )
        state_after = self._get_venv_state()

        removed_meta_dirs = {name for name in state_before if name not in state_after}
        # removed meta dirs are expected when upgrading
        for meta_dir_name in removed_meta_dirs:
            self._report_progress(f"Removing {parse_meta_dir_name(meta_dir_name)[0]}")
            dist_name, _version = parse_meta_dir_name(meta_dir_name)
            self._adapter.remove_dist(dist_name)

        new_meta_dirs = {name for name in state_after if name not in state_before}
        changed_meta_dirs = {
            name
            for name in state_after
            if name in state_before and state_after[name] != state_before[name]
        }

        if new_meta_dirs or changed_meta_dirs:
            self._report_progress("Starting to apply changes to the target.")

        if target:
            effective_target = target
        elif user:
            effective_target = self._adapter.get_user_packages_path()
        else:
            effective_target = self._adapter.get_default_target()

        for meta_dir in changed_meta_dirs:
            self._report_progress(f"Removing old version of {parse_meta_dir_name(meta_dir)[0]}")
            # if target is specified by --target or --user, then don't touch anything
            # besides corresponding directory, regardless of the sys.path and possible hiding
            dist_name, _version = parse_meta_dir_name(meta_dir)
            if target:
                # pip doesn't remove old dist with --target unless --upgrade is given
                if upgrade:
                    self._adapter.remove_dist(dist_name=dist_name, target=target)
            elif user:
                self._adapter.remove_dist(
                    dist_name=dist_name, target=self._adapter.get_user_packages_path()
                )
            else:
                # remove the all installations of this dist, which would hide the new installation
                self._adapter.remove_dist(
                    dist_name=dist_name, target=effective_target, above_target=True
                )

        for meta_dir in new_meta_dirs | changed_meta_dirs:
            self._upload_dist_by_meta_dir(meta_dir, effective_target, compile, mpy_cross)

        if new_meta_dirs or changed_meta_dirs:
            self._report_progress("All changes applied.")

    def uninstall(
        self,
        packages: Optional[List[str]] = None,
        requirement_files: Optional[List[str]] = None,
        yes: bool = False,
        **_,
    ):
        args = ["uninstall", "--yes"]

        for rf in requirement_files or []:
            args += ["-r", rf]
        for package in packages or []:
            args.append(package)

        self._populate_venv()
        state_before = self._get_venv_state()
        self._invoke_pip(args)
        state_after = self._get_venv_state()

        removed_meta_dirs = {name for name in state_before if name not in state_after}
        if removed_meta_dirs:
            # NB! If you want to move confirmation back to pip process, then test the process
            # in Windows via Thonny
            if not yes:
                names = [parse_meta_dir_name(d)[0] for d in removed_meta_dirs]
                if input(f"Proceed removing {', '.join(names)} (Y/n) at target? ").lower() == "n":
                    return

            self._report_progress("Starting to apply changes to the target.")

        for meta_dir_name in removed_meta_dirs:
            self._report_progress(f"Removing {parse_meta_dir_name(meta_dir_name)[0]}")
            dist_name, _version = parse_meta_dir_name(meta_dir_name)
            self._adapter.remove_dist(dist_name)

        if removed_meta_dirs:
            self._report_progress("All changes applied.")

    def list(
        self,
        outdated: bool = False,
        uptodate: bool = False,
        not_required: bool = False,
        pre: bool = False,
        paths: Optional[List[str]] = None,
        user: bool = False,
        format: str = "columns",
        no_mp_org: Optional[bool] = False,
        index_url: Optional[str] = None,
        extra_index_urls: Optional[List[str]] = None,
        no_index: bool = False,
        find_links: Optional[str] = None,
        excludes: Optional[List[str]] = None,
        **_,
    ):
        args = ["list"]

        if outdated:
            args.append("--outdated")
        if uptodate:
            args.append("--uptodate")
        if not_required:
            args.append("--not-required")
        if pre:
            args.append("--pre")
        if format:
            args += ["--format", format]

        args += self._format_exclusion_args(excludes)

        self._populate_venv(paths=paths, user=user)

        self._invoke_pip_with_index_args(
            args,
            no_mp_org=no_mp_org,
            index_url=index_url,
            extra_index_urls=extra_index_urls,
            no_index=no_index,
            find_links=find_links,
        )

    def basic_list(self) -> Set[DistInfo]:
        """
        Allows listing without requiring the venv.
        """
        dists_by_name = self._adapter.list_dists()
        result = set()
        for name in dists_by_name:
            meta_dir_name, location = dists_by_name[name]
            name, version = parse_meta_dir_name(meta_dir_name)
            result.add(DistInfo(key=name, project_name=name, version=version, location=location))

        return result

    def show(self, packages: List[str], **_):
        self._populate_venv()
        self._invoke_pip(["show"] + packages)

    def freeze(
        self,
        paths: Optional[List[str]] = None,
        user: bool = False,
        excludes: Optional[List[str]] = None,
        **_,
    ):
        args = ["freeze"]

        args += self._format_exclusion_args(excludes)

        self._populate_venv(paths=paths, user=user)
        self._invoke_pip(args)

    def check(self, **_):
        self._populate_venv()
        self._invoke_pip(["check"])

    def download(
        self,
        specs: Optional[List[str]] = None,
        requirement_files: Optional[List[str]] = None,
        constraint_files: Optional[List[str]] = None,
        pre: bool = False,
        no_deps: bool = False,
        no_mp_org: bool = False,
        index_url: Optional[str] = None,
        extra_index_urls: Optional[List[str]] = None,
        no_index: bool = False,
        find_links: Optional[str] = None,
        dest: Optional[str] = None,
        **_,
    ):
        args = ["download"]

        if dest:
            args += ["--dest", dest]

        args += self._format_selection_args(
            specs=specs,
            requirement_files=requirement_files,
            constraint_files=constraint_files,
            pre=pre,
            no_deps=no_deps,
        )

        self._populate_venv()
        self._invoke_pip_with_index_args(
            args,
            no_mp_org=no_mp_org,
            index_url=index_url,
            extra_index_urls=extra_index_urls,
            no_index=no_index,
            find_links=find_links,
        )

    def wheel(
        self,
        specs: Optional[List[str]] = None,
        requirement_files: Optional[List[str]] = None,
        constraint_files: Optional[List[str]] = None,
        pre: bool = False,
        no_deps: bool = False,
        no_mp_org: bool = False,
        index_url: Optional[str] = None,
        extra_index_urls: Optional[List[str]] = None,
        no_index: bool = False,
        find_links: Optional[str] = None,
        wheel_dir: Optional[str] = None,
        **_,
    ):
        args = ["wheel"]

        if wheel_dir:
            args += ["--wheel-dir", wheel_dir]

        args += self._format_selection_args(
            specs=specs,
            requirement_files=requirement_files,
            constraint_files=constraint_files,
            pre=pre,
            no_deps=no_deps,
        )

        self._populate_venv()
        self._invoke_pip_with_index_args(
            args,
            no_mp_org=no_mp_org,
            index_url=index_url,
            extra_index_urls=extra_index_urls,
            no_index=no_index,
            find_links=find_links,
        )

    def cache(self, cache_command: str, **_) -> None:
        if cache_command == "purge":
            if os.path.exists(self._get_pipkin_cache_dir()):
                shutil.rmtree(self._get_pipkin_cache_dir())
        elif not os.path.exists(self._get_pipkin_cache_dir()):
            print(f"Cache dir ({self._get_pipkin_cache_dir()}) not created yet")
        elif cache_command == "dir":
            print(self._get_pipkin_cache_dir())
        else:
            self._ensure_venv()
            self._invoke_pip(["cache", cache_command])

    def close(self) -> None:
        if self._venv_lock is not None:
            # self._clear_venv()
            self._venv_lock.release()

    def _format_exclusion_args(self, excludes: Optional[List[str]]) -> List[str]:
        args = []
        for exclude in (excludes or []) + ["pip", "pkg_resources", "setuptools", "wheel"]:
            args += ["--exclude", exclude]

        return args

    def _format_selection_args(
        self,
        specs: Optional[List[str]],
        requirement_files: Optional[List[str]],
        constraint_files: Optional[List[str]],
        pre: bool,
        no_deps: bool,
    ):
        args = []

        for path in requirement_files or []:
            args += ["-r", path]
        for path in constraint_files or []:
            args += ["-c", path]

        if no_deps:
            args.append("--no-deps")
        if pre:
            args.append("--pre")

        args += specs or []

        return args

    def _upload_dist_by_meta_dir(
        self, meta_dir_name: str, target: str, compile: bool, mpy_cross: Optional[str]
    ) -> None:
        self._report_progress(f"Copying {parse_meta_dir_name(meta_dir_name)[0]}", end="")
        rel_record_path = os.path.join(meta_dir_name, "RECORD")
        record_path = os.path.join(self._get_venv_site_packages_path(), rel_record_path)
        assert os.path.exists(record_path)

        target_record_lines = []

        with open(record_path, encoding=META_ENCODING) as fp:
            record_lines = fp.read().splitlines()

        for line in record_lines:
            rel_path = line.split(",")[0]
            # don't consider files installed to e.g. bin-directory
            if rel_path.startswith(".."):
                continue

            # don't consider absolute paths
            if os.path.isabs(rel_path):
                logger.warning("Skipping absolute path %s", rel_path)
                continue

            # only consider METADATA from meta dir
            if rel_path.startswith(meta_dir_name) and os.path.basename(rel_path) != "METADATA":
                continue

            full_path = os.path.normpath(
                os.path.join(self._get_venv_site_packages_path(), rel_path)
            )

            full_device_path = self._adapter.join_path(target, self._adapter.normpath(rel_path))

            if full_path.endswith(".py") and compile:
                self._compile_with_mpy_cross(
                    full_path, self._get_compiled_path(full_path), mpy_cross
                )
                # forget about the .py file
                full_path = self._get_compiled_path(full_path)
                full_device_path = self._get_compiled_path(full_device_path)
                rel_path = self._get_compiled_path(rel_path)

            with open(full_path, "rb") as source_fp:
                content = source_fp.read()

            if rel_path.startswith(meta_dir_name) and os.path.basename(rel_path) == "METADATA":
                content = self._trim_metadata(content)

            self._adapter.write_file(full_device_path, content)
            self._report_progress(".", end="")
            target_record_lines.append(self._adapter.normpath(rel_path) + ",,")

        # add RECORD (without hashes)
        target_record_lines.append(self._adapter.normpath(rel_record_path) + ",,")
        full_device_record_path = self._adapter.join_path(
            target, self._adapter.normpath(rel_record_path)
        )
        self._adapter.write_file(
            full_device_record_path, "\n".join(target_record_lines).encode(META_ENCODING)
        )

        # add linebreak for the report
        self._report_progress("")

    def _trim_metadata(self, content: bytes) -> bytes:
        # TODO:
        return content

    def _get_compiled_path(self, source_path: str) -> str:
        assert source_path.endswith(".py"), f"Source path: {source_path}"
        return source_path[: -len(".py")] + ".mpy"

    def _ensure_venv(self) -> None:
        if self._venv_lock is not None:
            return

        self._venv_lock, self._venv_dir = self._prepare_venv()

    def _prepare_venv(self) -> Tuple[BaseFileLock, str]:
        path = self._compute_venv_path()
        if not os.path.exists(path):
            self._report_progress("Preparing working environment ...")
            logger.info("Start preparing working environment at %s ...", path)
            venv_cmd = [
                sys.executable,
                "-I",
                "-m",
                "venv",
                path,
            ]
            subprocess.check_call(
                venv_cmd,
                executable=venv_cmd[0],
                stdin=subprocess.DEVNULL,
            )
            logger.info("Done creating venv")
            assert os.path.exists(path)
            pip_cmd = [
                get_venv_executable(path),
                "-I",
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                "--no-warn-script-location",
                "--upgrade",
                "pip==22.2.2",
                "setuptools==65.4.1",
                "wheel==0.38.4",
            ]
            subprocess.check_call(
                pip_cmd,
                executable=pip_cmd[0],
                stdin=subprocess.DEVNULL,
            )
            self._patch_pip(path)
            logger.info("Done preparing working environment.")
        else:
            logger.debug("Using existing working environment at %s", path)

        lock = FileLock(os.path.join(path, "pipkin.lock"))
        try:
            lock.acquire(timeout=0.05)
        except filelock.Timeout:
            raise UserError(
                "Could not get exclusive access to the working environment. "
                "Is there another pipkin instance running?"
            )
        logger.debug("Received lock on the working environment")

        return lock, path

    def _get_venv_site_packages_path(self) -> str:
        return get_venv_site_packages_path(self._venv_dir)

    def _patch_pip(self, venv_path: str) -> None:
        sp_cmd = [
            get_venv_executable(venv_path),
            "-c",
            "import sysconfig; print(sysconfig.get_paths()['purelib'])",
        ]
        site_packages_path = subprocess.check_output(
            sp_cmd,
            executable=sp_cmd[0],
            stdin=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()

        pip_init_path = os.path.join(site_packages_path, "pip", "__init__.py")

        patch = """
import os
import pip._vendor.packaging.markers
import pip._vendor.distlib.markers

ENV_VAR_PREFIX = "pip_marker_"

def patch_context(context):
    for name in os.environ:
        if name.startswith(ENV_VAR_PREFIX):
            marker_name = name[len(ENV_VAR_PREFIX):]
            value =  os.environ[name]
            context[marker_name] = value


def patch_context_function(fun):
    def patched_context_function():
        context = fun()
        patch_context(context)
        return context
    
    return patched_context_function

pip._vendor.packaging.markers.default_environment = \
    patch_context_function(pip._vendor.packaging.markers.default_environment)
pip._vendor.distlib.markers.DEFAULT_CONTEXT = \
    patch_context(pip._vendor.distlib.markers.DEFAULT_CONTEXT)        

"""
        logger.info("Patching %r", pip_init_path)
        with open(pip_init_path, "a", encoding="utf-8") as fp:
            fp.write(patch)

    def _clear_venv(self) -> None:
        sp_path = self._get_venv_site_packages_path()
        logger.debug("Clearing %s", sp_path)
        for name in os.listdir(sp_path):
            full_path = os.path.join(sp_path, name)
            if self._is_initial_venv_item(name):
                logger.debug("skipping %r", name)
                continue
            elif os.path.isfile(full_path):
                logger.debug("removing file %r", name)
                os.remove(full_path)
            else:
                logger.debug("removing directory %r", name)
                assert os.path.isdir(full_path)
                shutil.rmtree(full_path)

    def _populate_venv(self, paths: Optional[List[str]] = None, user: bool = False) -> None:
        """paths and user should be used only with list and freeze commands"""
        logger.debug("Start populating venv")
        self._ensure_venv()
        # TODO: try to re-use the state from the previous command executed in the same session.
        assert not (paths and user)
        if user:
            effective_paths = [self._adapter.get_user_packages_path()]
        else:
            effective_paths = paths
        self._clear_venv()
        dist_infos = self._adapter.list_dists(effective_paths)
        for name in dist_infos:
            meta_dir_name, original_path = dist_infos[name]
            self._prepare_dummy_dist(meta_dir_name, original_path)
        logger.debug("Done populating venv")

    def _prepare_dummy_dist(self, meta_dir_name: str, original_path: str) -> None:
        sp_path = self._get_venv_site_packages_path()
        meta_path = os.path.join(sp_path, meta_dir_name)
        os.mkdir(meta_path, 0o755)

        for name in ["METADATA"]:
            content = self._read_dist_meta_file(meta_dir_name, name, original_path)
            with open(os.path.join(meta_path, name), "bw") as meta_fp:
                meta_fp.write(content)

        # INSTALLER is mandatory according to https://www.python.org/dev/peps/pep-0376/
        with open(os.path.join(meta_path, "INSTALLER"), "w", encoding="utf-8") as installer_fp:
            installer_fp.write("pip\n")

        # create dummy RECORD
        with open(os.path.join(meta_path, "RECORD"), "w", encoding=META_ENCODING) as record_fp:
            for name in ["METADATA", "INSTALLER", "RECORD"]:
                record_fp.write(f"{meta_dir_name}/{name},,\n")

    def _read_dist_meta_file(
        self, meta_dir_name: str, file_name: str, original_container_path: str
    ) -> bytes:
        # TODO: add cache
        path = self._adapter.join_path(original_container_path, meta_dir_name, file_name)
        return self._adapter.read_file(path)

    def _compute_venv_path(self) -> str:
        try:
            # try to share the pip-execution-venv among all pipkin-running-venvs created from
            # same base executable
            exe = get_base_executable()
        except Exception:
            exe = sys.executable

        venv_name = hashlib.md5(str((exe, sys.version_info[0:2])).encode("utf-8")).hexdigest()
        return os.path.join(self._get_workspaces_dir(), venv_name)

    def _get_workspaces_dir(self) -> str:
        return os.path.join(self._get_pipkin_cache_dir(), "workspaces")

    def _get_pipkin_cache_dir(self) -> str:
        result = os.path.join(get_user_cache_dir(), "pipkin")
        if sys.platform == "win32":
            # Windows doesn't have separate user cache dir
            result = os.path.join(result, "cache")
        return result

    def _is_initial_venv_item(self, name: str) -> bool:
        return (
            name in INITIAL_VENV_FILES
            or name in INITIAL_VENV_DISTS
            or name.endswith(".dist-info")
            and name.split("-")[0] in INITIAL_VENV_DISTS
        )

    def _get_venv_state(self, root: str = None) -> Dict[str, float]:
        """Returns mapping from meta_dir names to modification timestamps of METADATA files"""
        if root is None:
            root = self._get_venv_site_packages_path()

        result = {}
        for item_name in os.listdir(root):
            if self._is_initial_venv_item(item_name):
                continue

            if item_name.endswith(".dist-info"):
                metadata_full_path = os.path.join(root, item_name, "METADATA")
                assert os.path.exists(metadata_full_path)
                result[item_name] = os.stat(metadata_full_path).st_mtime

        return result

    def _invoke_pip_with_index_args(
        self,
        pip_args: List[str],
        no_mp_org: bool,
        index_url: str,
        extra_index_urls: List[str],
        no_index: bool,
        find_links: Optional[str],
    ):
        if no_index:
            assert find_links
            self._invoke_pip(pip_args + ["--no-index", "--find-links", find_links])
        else:
            proxy = start_proxy(no_mp_org, index_url, extra_index_urls)
            logger.info("Using PipkinProxy at %s", proxy.get_index_url())

            index_args = ["--index-url", proxy.get_index_url()]
            if find_links:
                index_args += ["--find-links", find_links]

            try:
                self._invoke_pip(pip_args + index_args)
            finally:
                proxy.shutdown()

    def _invoke_pip(self, args: List[str]) -> None:
        pip_cmd = [get_venv_executable(self._venv_dir), "-I", "-m", "pip"]

        if not self._tty:
            pip_cmd += ["--no-color"]

        pip_cmd += [
            "--disable-pip-version-check",
            "--trusted-host",
            "127.0.0.1",
        ] + args
        logger.debug("Calling pip: %s", " ".join(shlex.quote(arg) for arg in pip_cmd))

        env = {key: os.environ[key] for key in os.environ if not key.startswith("PIP_")}
        env["PIP_CACHE_DIR"] = self._get_pipkin_cache_dir()

        subprocess.check_call(pip_cmd, executable=pip_cmd[0], env=env, stdin=subprocess.DEVNULL)

    def _compile_with_mpy_cross(
        self, source_path: str, target_path: str, mpy_cross_path: Optional[str]
    ) -> None:
        if mpy_cross_path is None:
            mpy_cross_path = self._ensure_mpy_cross()

        # user-provided executable is assumed to have been validated with proper error messages in main()
        assert os.path.exists
        assert os.access(mpy_cross_path, os.X_OK)
        args = (
            [mpy_cross_path] + self._adapter.get_mpy_cross_args() + ["-o", target_path, source_path]
        )
        subprocess.check_call(args, executable=args[0], stdin=subprocess.DEVNULL)

    def _ensure_mpy_cross(self) -> str:
        impl_name, ver_prefix = self._adapter.get_implementation_name_and_version_prefix()
        path = self._get_mpy_cross_path(impl_name, ver_prefix)
        if not os.path.exists(path):
            self._download_mpy_cross(impl_name, ver_prefix, path)
        return path

    def _download_mpy_cross(
        self, implementation_name: str, version_prefix: str, target_path: str
    ) -> None:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        meta_url = f"https://raw.githubusercontent.com/aivarannamaa/pipkin/master/data/{implementation_name}-mpy-cross.json"
        with urlopen(url=meta_url) as fp:
            meta = json.load(fp)

        if version_prefix not in meta:
            raise UserError(f"Can't find mpy-cross for {implementation_name} {version_prefix}")

        version_data = meta[version_prefix]

        if sys.platform == "win32":
            os_marker = "windows"
        elif sys.platform == "darwin":
            os_marker = "macos"
        elif sys.platform == "linux":
            os_marker = "linux"
        else:
            raise AssertionError(f"Unexpected sys.platform {sys.platform}")

        full_marker = f"{os_marker}-{platform.machine()}"

        if full_marker not in version_data:
            raise UserError(
                f"Can't find {full_marker} mpy-cross for {implementation_name} {version_prefix}"
            )

        download_url = version_data[full_marker]

        urllib.request.urlretrieve(download_url, target_path)
        os.chmod(target_path, os.stat(target_path).st_mode | stat.S_IEXEC)

    def _get_mpy_cross_path(self, implementation_name: str, version_prefix: str) -> str:
        basename = f"mpy-cross_{implementation_name}_{version_prefix}"
        if sys.platform == "win32":
            basename += ".exe"

        return os.path.join(self._get_pipkin_cache_dir(), "mpy-cross", basename)

    def _report_progress(self, msg: str, end="\n") -> None:
        if not self._quiet:
            print(msg, end=end)
            sys.stdout.flush()
