import argparse
import sys
from typing import Any, List, Optional

from pipkin import __version__


def parse_arguments(raw_args: Optional[List[str]] = None) -> Any:
    if raw_args is None:
        raw_args = sys.argv[1:]

    main_parser = argparse.ArgumentParser(
        description="Tool for managing MicroPython and CircuitPython packages",
        allow_abbrev=False,
        add_help=False,
    )

    general_group = main_parser.add_argument_group(title="general")

    general_group.add_argument(
        "-h",
        "--help",
        help="Show this help message and exit",
        action="help",
    )
    general_group.add_argument(
        "-V",
        "--version",
        help="Show program version and exit",
        action="version",
        version=__version__,
    )
    verbosity_group = general_group.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        help="Show more details about the process",
        action="store_true",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        help="Don't show non-error output",
        action="store_true",
    )

    connection_group = main_parser.add_argument_group(
        title="target selection (pick one or let pipkin autodetect the port or mount)"
    )
    connection_exclusive_group = connection_group.add_mutually_exclusive_group()

    connection_exclusive_group.add_argument(
        "-p",
        "--port",
        help="Serial port of the target device",
        metavar="<port>",
    )
    connection_exclusive_group.add_argument(
        "-m",
        "--mount",
        help="Mount point (volume, disk, drive) of the target device",
        metavar="<path>",
    )
    connection_exclusive_group.add_argument(
        "-d",
        "--dir",
        help="Directory in the local filesystem",
        metavar="<path>",
    )
    # connection_exclusive_group.add_argument(
    #     "-e",
    #     "--exe",
    #     help="Interpreter executable (Unix or Windows port)",
    #     metavar="<path>",
    # )

    # sub-parsers
    subparsers = main_parser.add_subparsers(
        title="commands",
        description='Use "pipkin <command> -h" for usage help of a command ',
        dest="command",
        required=True,
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install packages.",
        description="Installs upip or pip compatible distribution packages onto "
        "a MicroPython/CircuitPython device  or into a local directory.",
    )

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall packages.")
    list_parser = subparsers.add_parser("list", help="List installed packages.")
    show_parser = subparsers.add_parser(
        "show", help="Show information about one or more installed packages."
    )
    freeze_parser = subparsers.add_parser(
        "freeze", help="Output installed packages in requirements format."
    )
    _check_parser = subparsers.add_parser(
        "check", help="Verify installed packages have compatible dependencies."
    )
    download_parser = subparsers.add_parser("download", help="Download packages.")
    wheel_parser = subparsers.add_parser(
        "wheel", help="Build Wheel archives for your requirements and dependencies."
    )
    cache_parser = subparsers.add_parser("cache", help="Inspect and manage pipkin cache.")

    # common options
    for parser in [install_parser, download_parser, wheel_parser]:
        parser.add_argument(
            "specs",
            help="Package specification, eg. 'micropython-os' or 'micropython-os>=0.6'",
            nargs="*",
            metavar="<spec>",
        )

        specs_group = parser.add_argument_group(title="package selection")

        specs_group.add_argument(
            "-r",
            "--requirement",
            help="Install from the given requirements file.",
            nargs="*",
            dest="requirement_files",
            metavar="<file>",
            default=[],
        )
        specs_group.add_argument(
            "-c",
            "--constraint",
            help="Constrain versions using the given constraints file.",
            nargs="*",
            dest="constraint_files",
            metavar="<file>",
            default=[],
        )
        specs_group.add_argument(
            "--no-deps",
            help="Don't install package dependencies.",
            action="store_true",
        )
        specs_group.add_argument(
            "--pre",
            help="Include pre-release and development versions. By default, pipkin only finds stable versions.",
            action="store_true",
        )

    # index-related
    for parser in [install_parser, download_parser, wheel_parser, list_parser]:
        index_group = parser.add_argument_group(title="index selection")
        index_group.add_argument(
            "-i",
            "--index-url",
            help="Base URL of the Python Package Index (default https://pypi.org/simple).",
            metavar="<url>",
        )
        index_group.add_argument(
            "--extra-index-url",
            help="Extra URLs of package indexes to use in addition to --index-url.",
            nargs="*",
            dest="extra_index_urls",
            default=[],
            metavar="<url>",
        )
        index_group.add_argument(
            "--no-index",
            help="Ignore package index (only looking at --find-links URLs instead).",
            action="store_true",
        )
        index_group.add_argument(
            "--no-mp-org",
            help="Don't let micropython.org/pi override other indexes.",
            action="store_true",
        )
        index_group.add_argument(
            "-f",
            "--find-links",
            help="If a URL or path to an html file, then parse for links to archives such as sdist "
            "(.tar.gz) or wheel (.whl) files. If a local path or "
            "file:// URL that's a directory, then look for archives in the directory listing.",
            metavar="<url|file|dir>",
        )

    for parser in [uninstall_parser, show_parser]:
        parser.add_argument(
            "packages",
            help="Package name",
            nargs="*",
            metavar="<name>",
        )

    for parser in [list_parser, freeze_parser]:
        # parser.add_argument(
        #     "--user",
        #     help="Only output packages installed in user-site. Relevant with Unix and Windows ports",
        #     action="store_true",
        # )
        # parser.add_argument(
        #     "--path",
        #     help="Restrict to the specified installation path for listing packages.",
        #     nargs="*",
        #     dest="paths",
        #     metavar="<path>",
        #     default=[],
        # )
        parser.add_argument(
            "--exclude",
            help="Exclude specified package from the output.",
            nargs="*",
            dest="excludes",
            metavar="<package>",
            default=[],
        )

    # install_parser.add_argument(
    #     "-t",
    #     "--target",
    #     help="Target directory in the target filesystem (eg. /lib)",
    #     metavar="<dir>",
    # )
    # install_parser.add_argument(
    #     "--user",
    #     help="Install to the Python user install directory for target platform. "
    #     "Only relevant with Unix and Windows ports",
    #     action="store_true",
    # )
    install_parser.add_argument(
        "-U",
        "--upgrade",
        help="Upgrade all specified packages to the newest available version. "
        "The handling of dependencies depends on the upgrade-strategy used.",
        action="store_true",
    )
    install_parser.add_argument(
        "--upgrade-strategy",
        help="Determines how dependency upgrading should be handled [default: only-if-needed].\n"
        "'eager' - dependencies are upgraded regardless of whether the currently installed "
        "version satisfies the requirements of the upgraded package(s).\n"
        "'only-if-needed' - are upgraded only when they do not satisfy the requirements of the "
        "upgraded package(s).",
        choices=["only-if-needed", "eager"],
        default="only-if-needed",
        metavar="<upgrade_strategy>",
    )
    install_parser.add_argument(
        "--force-reinstall",
        help="Reinstall all packages even if they are already up-to-date.",
        action="store_true",
    )
    install_parser.add_argument(
        "--compile",
        help="Compile and install mpy files.",
        action="store_true",
    )

    uninstall_parser.add_argument(
        "-r",
        "--requirement",
        help="Uninstall all the packages listed in the given requirements file.",
        nargs="*",
        dest="requirement_files",
        metavar="<file>",
        default=[],
    )

    uninstall_parser.add_argument(
        "-y",
        "--yes",
        help="Don't ask for confirmation of uninstall deletions.",
        action="store_true",
    )

    list_parser.add_argument(
        "-o",
        "--outdated",
        help="List outdated packages",
        action="store_true",
    )
    list_parser.add_argument(
        "-u",
        "--uptodate",
        help="List uptodate packages",
        action="store_true",
    )
    list_parser.add_argument(
        "--pre",
        help="Also consider pre-release and development versions when deciding whether package is outdated or uptodate.",
        action="store_true",
    )
    list_parser.add_argument(
        "--not-required",
        help="List packages that are not dependencies of installed packages.",
        action="store_true",
    )
    list_parser.add_argument(
        "--format",
        help="Select the output format among: columns (default), freeze, or json",
        choices=["columns", "freeze", "json"],
        default="columns",
        metavar="<list_format>",
    )

    download_parser.add_argument(
        "-d",
        "--dest",
        help="Download packages into <dir>. Default: current directory.",
        default=".",
        metavar="<dir>",
    )

    wheel_parser.add_argument(
        "-w",
        "--wheel-dir",
        help="Build wheels into <dir>, where the default is the current working directory.",
        default=".",
        metavar="<dir>",
    )

    cache_parser.add_argument("cache_command", choices=["dir", "info", "list", "purge"])

    args = main_parser.parse_args(args=raw_args)

    # print("ARGS", args)
    return args
