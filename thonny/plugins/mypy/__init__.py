import re
from logging import getLogger
from typing import Dict, List, Optional

from thonny import get_runner, get_workbench
from thonny.assistance import (
    ChatContext,
    ProgramAnalyzerResponseItem,
    ProgramAnalyzerResponseItemType,
    SubprocessProgramAnalyzer,
)
from thonny.running import get_front_interpreter_for_subprocess

logger = getLogger(__name__)


class MyPyAnalyzer(SubprocessProgramAnalyzer):
    def parse_output_line(
        self, line: str, context: ChatContext
    ) -> Optional[ProgramAnalyzerResponseItem]:
        m = re.match(r"(.*?):(\d+)(:(\d+))?:(.*?):(.*)", line.strip())
        if m is not None:
            message = m.group(6).strip()
            if message == "invalid syntax":
                return None

            filename = m.group(1)
            if filename not in [context.main_file_path] + context.imported_file_paths:
                logger.warning("MyPy: " + line)
                return None

            line_num = int(m.group(2))
            kind = (m.group(5).strip(),)  # always "error" ?

            if m.group(3):
                # https://github.com/thonny/thonny/issues/598
                column = max(int(m.group(4)) - 1, 0)
            else:
                column = None

            # TODO: find the way to link to the explanation at https://mypy.readthedocs.io/en/stable/error_code_list.html
            return ProgramAnalyzerResponseItem(
                message, ProgramAnalyzerResponseItemType.WARNING, filename, line_num, column
            )
        else:
            logger.error("Can't parse MyPy line: " + line.strip())
            return None

    def get_command_line(self, context: ChatContext) -> List[str]:
        return [
            get_front_interpreter_for_subprocess(),
            "-m",
            "mypy",
            "--ignore-missing-imports",
            "--check-untyped-defs",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--show-column-numbers",
            "--no-implicit-optional",
            "--python-executable",
            get_runner().get_backend_proxy().get_target_executable(),
            "--warn-unreachable",
            "--allow-redefinition",
            "--strict-equality",
            "--no-color-output",
            "--no-error-summary",
            context.main_file_path,
        ] + context.imported_file_paths

    def get_env(self) -> Dict[str, str]:
        env = super().get_env()
        mypypath = get_workbench().get_option("assistance.mypypath")
        if mypypath:
            return env | {"MYPYPATH": mypypath}

        return env


def load_plugin():
    get_workbench().add_assistant("mypy", MyPyAnalyzer())
    get_workbench().set_default("assistance.use_mypy", True)
    get_workbench().set_default("assistance.mypypath", None)
