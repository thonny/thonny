import re
import os.path
import subprocess
import sys
from typing import Iterable

from thonny import get_runner, ui_utils
from thonny.assistance import SubprocessProgramAnalyzer, add_program_analyzer
from thonny.running import get_frontend_python
import logging


class MyPyAnalyzer(SubprocessProgramAnalyzer):
    def start_analysis(
        self, main_file_path, imported_file_paths: Iterable[str]
    ) -> None:

        args = [
            get_frontend_python(),
            "-m",
            "mypy",
            "--ignore-missing-imports",
            "--check-untyped-defs",
            "--warn-redundant-casts",
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
            args.insert(4, get_runner().get_executable())
        
        env = os.environ.copy()
        env["MYPYPATH"] = os.path.join(os.path.dirname(__file__), "typeshed_extras")
        
        self._proc = ui_utils.popen_with_ui_thread_callback(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            on_completion=self._parse_and_output_warnings,
        )

    def _parse_and_output_warnings(self, pylint_proc, out_lines, err_lines):
        if err_lines:
            logging.getLogger("thonny").warning("MyPy: " + "".join(err_lines))
            
        warnings = []
        for line in out_lines:
            m = re.match(r"(.*?):(\d+)(:(\d+))?:(.*?):(.*)", line.strip())
            if m is not None:
                message = m.group(6).strip()
                if message == "invalid syntax":
                    continue  # user will see this as Python error
                
                filename = m.group(1)
                
                atts = {
                    "filename": filename,
                    "lineno": int(m.group(2)),
                    "kind": m.group(5).strip(),  # always "error" ?
                    "msg": message,
                    "group": "warnings",
                }
                if m.group(3):
                    atts["col_offset"] = int(m.group(4))-1
                    
                # TODO: add better categorization and explanation
                atts["symbol"] = "mypy-" + atts["kind"]
                warnings.append(atts)
            else:
                logging.error("Can't parse MyPy line: " + line.strip())
                

        self.completion_handler(self, warnings)


def load_plugin():
    add_program_analyzer(MyPyAnalyzer)
