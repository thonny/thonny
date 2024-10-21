from logging import getLogger
from typing import List, Optional

from thonny import get_workbench
from thonny.plugins.pylint.messages import checks_by_id
from thonny.program_analysis import (
    ProgramAnalyzerResponseItem,
    ProgramAnalyzerResponseItemType,
    SubprocessProgramAnalyzer,
)
from thonny.running import get_front_interpreter_for_subprocess

logger = getLogger(__name__)

RESULT_MARKER = "ForThonny: "


class PylintAnalyzer(SubprocessProgramAnalyzer):

    def get_command_line(self, main_file_path: str) -> List[str]:
        relevant_symbols = {
            checks_by_id[key]["msg_sym"]
            for key in checks_by_id
            if checks_by_id[key]["usage"] == "warning"
        }

        if "bad-python3-import" in relevant_symbols:
            # https://github.com/PyCQA/pylint/issues/2453
            # TODO: allow if this is fixed in minimum version
            relevant_symbols.remove("bad-python3-import")

        # remove user-disabled checks
        relevant_symbols = relevant_symbols - set(
            get_workbench().get_option("assistance.disabled_checks")
        )

        # TODO:
        ignored_modules = {"turtle"}  # has dynamically generated attributes

        options = [
            # "--rcfile=None", # TODO: make it ignore any rcfiles that can be somewhere
            "--persistent=n",
            # "--confidence=HIGH", # Leave empty to show all. Valid levels: HIGH, INFERENCE, INFERENCE_FAILURE, UNDEFINED
            # "--disable=missing-docstring,invalid-name,trailing-whitespace,trailing-newlines,missing-final-newline,locally-disabled,suppressed-message",
            "--disable=all",
            "--enable=" + ",".join(relevant_symbols),
            "--ignored-modules=" + ",".join(ignored_modules),
            "--max-line-length=120",
            "--output-format=text",
            "--reports=n",
            "--msg-template="
            + RESULT_MARKER
            + "{abspath},,{line},,{column},,{symbol},,{msg},,{msg_id},,{C}",
        ]

        return [get_front_interpreter_for_subprocess(), "-m", "pylint"] + options + [main_file_path]

    def parse_output_line(self, line: str) -> Optional[ProgramAnalyzerResponseItem]:
        # TODO: get rid of non-error
        """
        err = (
            "".join(err_lines)
            .replace("No config file found, using default configuration", "")
            .strip()
        )
        """
        if line.startswith(RESULT_MARKER):
            # See https://github.com/thonny/thonny/issues/2359 for the background of this format
            atts_tuple = line[len(RESULT_MARKER) :].strip().split(",,")
            if len(atts_tuple) != 7:
                logger.error("Can't parse Pylint line %r (%r)", line, atts_tuple)
                return None
            try:
                filename = atts_tuple[0]
                lineno = int(atts_tuple[1])
                col_offset = int(atts_tuple[2])
                symbol = atts_tuple[3]
                msg = atts_tuple[4]
                msg_id = atts_tuple[5]
                category = atts_tuple[6]
            except ValueError:
                logger.exception("Can't parse Pylint line %r (%r)", line, atts_tuple)
                return None

            if msg_id not in checks_by_id:
                logger.warning("Unknown msg_id %r", msg_id)
                return None

            check = checks_by_id[msg_id]
            if check.get("tho_xpln"):
                explanation = check["tho_xpln"]
            else:
                explanation = check["msg_xpln"]

            if explanation.startswith("Used when an "):
                explanation = "It looks like the " + explanation[(len("Used when an ")) :]
            elif explanation.startswith("Emitted when an "):
                explanation = "It looks like the " + explanation[(len("Emitted when an ")) :]
            elif explanation.startswith("Used when a "):
                explanation = "It looks like the " + explanation[(len("Used when a ")) :]
            elif explanation.startswith("Emitted when a "):
                explanation = "It looks like the " + explanation[(len("Emitted when a ")) :]
            elif explanation.startswith("Used when "):
                explanation = "It looks like " + explanation[(len("Used when ")) :]
            elif explanation.startswith("Emitted when "):
                explanation = "It looks like " + explanation[(len("Emitted when ")) :]

            if check.get("tho_xpln_rst"):
                explanation_rst = check["tho_xpln_rst"]

            if category in ("I", "F"):
                msg = "INTERNAL ERROR when analyzing the code: " + msg

            # atts["more_info_url"] = "http://pylint-messages.wikidot.com/messages:%s" % atts["msg_id"].lower()
            return ProgramAnalyzerResponseItem(
                msg, ProgramAnalyzerResponseItemType.WARNING, filename, lineno, col_offset
            )


def load_plugin():
    get_workbench().add_program_analyzer("Pylint", PylintAnalyzer())
