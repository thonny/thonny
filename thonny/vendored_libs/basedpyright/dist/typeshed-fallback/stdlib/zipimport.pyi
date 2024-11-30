"""
zipimport provides support for importing Python modules from Zip archives.

This module exports three objects:
- zipimporter: a class; its constructor takes a path to a Zip archive.
- ZipImportError: exception raised by zipimporter objects. It's a
  subclass of ImportError, so it can be caught as ImportError, too.
- _zip_directory_cache: a dict, mapping archive paths to zip directory
  info dicts, as used in zipimporter._files.

It is usually not needed to use the zipimport module explicitly; it is
used by the builtin import mechanism for sys.path items that are paths
to Zip archives.
"""

import sys
from _typeshed import StrOrBytesPath
from importlib.abc import ResourceReader
from importlib.machinery import ModuleSpec
from types import CodeType, ModuleType
from typing_extensions import deprecated

if sys.version_info >= (3, 10):
    from _frozen_importlib_external import _LoaderBasics
else:
    _LoaderBasics = object

__all__ = ["ZipImportError", "zipimporter"]

class ZipImportError(ImportError): ...

class zipimporter(_LoaderBasics):
    """
    zipimporter(archivepath) -> zipimporter object

    Create a new zipimporter instance. 'archivepath' must be a path to
    a zipfile, or to a specific path inside a zipfile. For example, it can be
    '/tmp/myimport.zip', or '/tmp/myimport.zip/mydirectory', if mydirectory is a
    valid directory inside the archive.

    'ZipImportError is raised if 'archivepath' doesn't point to a valid Zip
    archive.

    The 'archive' attribute of zipimporter objects contains the name of the
    zipfile targeted.
    """
    archive: str
    prefix: str
    if sys.version_info >= (3, 11):
        def __init__(self, path: str) -> None: ...
    else:
        def __init__(self, path: StrOrBytesPath) -> None: ...

    if sys.version_info < (3, 12):
        def find_loader(self, fullname: str, path: str | None = None) -> tuple[zipimporter | None, list[str]]: ...  # undocumented
        def find_module(self, fullname: str, path: str | None = None) -> zipimporter | None: ...

    def get_code(self, fullname: str) -> CodeType: ...
    def get_data(self, pathname: str) -> bytes: ...
    def get_filename(self, fullname: str) -> str: ...
    def get_resource_reader(self, fullname: str) -> ResourceReader | None: ...  # undocumented
    def get_source(self, fullname: str) -> str | None: ...
    def is_package(self, fullname: str) -> bool: ...
    @deprecated("Deprecated since 3.10; use exec_module() instead")
    def load_module(self, fullname: str) -> ModuleType: ...
    if sys.version_info >= (3, 10):
        def exec_module(self, module: ModuleType) -> None: ...
        def create_module(self, spec: ModuleSpec) -> None: ...
        def find_spec(self, fullname: str, target: ModuleType | None = None) -> ModuleSpec | None: ...
        def invalidate_caches(self) -> None: ...
