import logging
import os.path
import re
import subprocess
import sys
from typing import Iterable

from thonny import get_runner, get_workbench, ui_utils
from thonny.assistance import SubprocessProgramAnalyzer, add_program_analyzer
from thonny.running import get_interpreter_for_subprocess

logger = logging.getLogger(__name__)


class MyPyAnalyzer(SubprocessProgramAnalyzer):
    def is_enabled(self):
        return get_workbench().get_option("assistance.use_mypy")

    def start_analysis(self, main_file_path, imported_file_paths: Iterable[str]) -> None:

        self.interesting_files = [main_file_path] + list(imported_file_paths)

        args = [
            get_interpreter_for_subprocess(),
            "-m",
            "mypy",
            "--ignore-missing-imports",
            "--check-untyped-defs",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--show-column-numbers",
            main_file_path,
        ] + list(imported_file_paths)

        # TODO: ignore "... need type annotation" messages

        from mypy.version import __version__

        try:
            ver = tuple(map(int, __version__.split(".")))
        except Exception:
            ver = (0, 470)  # minimum required version

        if ver >= (0, 520):
            args.insert(3, "--no-implicit-optional")

        if ver >= (0, 590):
            args.insert(3, "--python-executable")
            args.insert(4, get_runner().get_local_executable())

        if ver >= (0, 730):
            args.insert(3, "--warn-unreachable")
            args.insert(3, "--allow-redefinition")
            args.insert(3, "--strict-equality")
            args.insert(3, "--no-color-output")
            args.insert(3, "--no-error-summary")

        env = os.environ.copy()
        mypypath = get_workbench().get_option("assistance.mypypath")
        if mypypath:
            env["MYPYPATH"] = mypypath

        self._proc = ui_utils.popen_with_ui_thread_callback(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            on_completion=self._parse_and_output_warnings,
            # Specify a cwd which is not ancestor of user files.
            # This gives absolute filenames in the output.
            # Note that mypy doesn't accept when cwd is sys.prefix
            # or dirname(sys.executable)
            cwd=os.path.dirname(__file__),
        )

    def _parse_and_output_warnings(self, pylint_proc, out_lines, err_lines):
        if err_lines:
            logger.warning("MyPy: " + "".join(err_lines))

        warnings = []
        for line in out_lines:
            m = re.match(r"(.*?):(\d+)(:(\d+))?:(.*?):(.*)", line.strip())
            if m is not None:
                message = m.group(6).strip()
                if message == "invalid syntax":
                    continue  # user will see this as Python error

                filename = m.group(1)
                if filename not in self.interesting_files:
                    logger.warning("MyPy: " + line)
                    continue

                atts = {
                    "filename": filename,
                    "lineno": int(m.group(2)),
                    "kind": m.group(5).strip(),  # always "error" ?
                    "msg": message,
                    "group": "warnings",
                }
                if m.group(3):
                    # https://github.com/thonny/thonny/issues/598
                    atts["col_offset"] = max(int(m.group(4)) - 1, 0)

                # TODO: add better categorization and explanation
                atts["symbol"] = "mypy-" + atts["kind"]
                warnings.append(atts)
            else:
                logging.error("Can't parse MyPy line: " + line.strip())

        self.completion_handler(self, warnings)


def load_plugin():
    add_program_analyzer(MyPyAnalyzer)
    get_workbench().set_default("assistance.use_mypy", True)
    get_workbench().set_default("assistance.mypypath", None)
