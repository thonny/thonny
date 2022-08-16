import ast
import subprocess
from logging import getLogger

from thonny import get_workbench, ui_utils
from thonny.assistance import SubprocessProgramAnalyzer, add_program_analyzer
from thonny.plugins.pylint.messages import checks_by_id
from thonny.running import get_front_interpreter_for_subprocess

logger = getLogger(__name__)

RESULT_MARKER = "ForThonny: "


class PylintAnalyzer(SubprocessProgramAnalyzer):
    def is_enabled(self):
        return get_workbench().get_option("assistance.use_pylint")

    def start_analysis(self, main_file_path, imported_file_paths):
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

        # disallow unused globals only in main script
        """
        Not good idea, because unused * imports also count as unused global vars
        from pylint.__pkginfo__ import numversion

        if not imported_file_paths and numversion >= (1, 7):
            # (unfortunately can't separate main script when user modules are present)
            options.append("--allow-global-unused-variables=no")
        """

        self._proc = ui_utils.popen_with_ui_thread_callback(
            [get_front_interpreter_for_subprocess(), "-m", "pylint"]
            + options
            + [main_file_path]
            + list(imported_file_paths),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            on_completion=self._parse_and_output_warnings,
        )

    def _parse_and_output_warnings(self, pylint_proc, out_lines, err_lines):
        # print("COMPL", out, err)
        # get rid of non-error
        err = (
            "".join(err_lines)
            .replace("No config file found, using default configuration", "")
            .strip()
        )

        if err:
            logger.error("Pylint: " + err)

        warnings = []
        for line in out_lines:
            if line.startswith(RESULT_MARKER):
                # See https://github.com/thonny/thonny/issues/2359 for the background of this format
                atts_tuple = line[len(RESULT_MARKER) :].strip().split(",,")
                if len(atts_tuple) != 7:
                    logger.error("Can't parse Pylint line %r (%r)", line, atts_tuple)
                    continue
                try:
                    atts = {
                        "filename": atts_tuple[0],
                        "lineno": int(atts_tuple[1]),
                        "col_offset": int(atts_tuple[2]),
                        "symbol": atts_tuple[3],
                        "msg": atts_tuple[4],
                        "msg_id": atts_tuple[5],
                        "category": atts_tuple[6],
                    }
                except ValueError:
                    logger.exception("Can't parse Pylint line %r (%r)", line, atts_tuple)
                    continue

                if atts["msg_id"] not in checks_by_id:
                    logger.warning("Unknown msg_id %r", atts["msg_id"])
                    continue

                check = checks_by_id[atts["msg_id"]]
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

                atts["explanation"] = explanation

                if check.get("tho_xpln_rst"):
                    atts["explanation_rst"] = check["tho_xpln_rst"]

                if atts["category"] in ("I", "F"):
                    atts["msg"] = "INTERNAL ERROR when analyzing the code: " + atts["msg"]

                # atts["more_info_url"] = "http://pylint-messages.wikidot.com/messages:%s" % atts["msg_id"].lower()
                warnings.append(atts)

        self.completion_handler(self, warnings)


def load_plugin():
    add_program_analyzer(PylintAnalyzer)
    get_workbench().set_default("assistance.use_pylint", True)
