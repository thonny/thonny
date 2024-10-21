import shlex
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from typing import Dict, List, Optional, cast

from thonny import get_workbench

logger = getLogger(__name__)


class ProgramAnalyzerResponseItemType(Enum):
    ERROR = "error"
    WARNING = "warning"
    # SUMMARY = "summary"


@dataclass
class ProgramAnalyzerResponseItem:
    message: str
    type: ProgramAnalyzerResponseItemType
    file: Optional[str]
    line: Optional[int]
    column: Optional[int]


class ProgramAnalyzer(ABC):
    @abstractmethod
    def analyze(self, main_file: str) -> None:
        """
        Called in a background thread.
        Stores results and generates ProgramAnalysisCompleted when done
        """

    @abstractmethod
    def get_results(self) -> Optional[List[ProgramAnalyzerResponseItem]]:
        """
        Called in UI thread
        """

    @abstractmethod
    def cancel(self) -> None:
        """
        Called in UI thread. Analyzer must be ready for next analysis before returning.
        """


class SubprocessProgramAnalyzer(ProgramAnalyzer, ABC):
    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._results: Optional[List[ProgramAnalyzerResponseItem]] = None

    def analyze(self, main_file: str) -> None:
        self.cancel()

        results = []

        self.start_subprocess(main_file)
        for line in self._proc.stdout:
            item = self.parse_output_line(line)
            if item is not None:
                results.append(item)

        err = cast(str, self._proc.stderr.read().strip())
        if err:
            results.append(
                ProgramAnalyzerResponseItem(
                    "INTERNAL ERROR: " + err,
                    ProgramAnalyzerResponseItemType.ERROR,
                    file=None,
                    line=None,
                    column=None,
                )
            )

        self._results = results
        get_workbench().queue_event(
            "ProgramAnalysisCompleted", event=dict(analyzer_class=type(self).__name__)
        )

    def get_results(self) -> Optional[List[ProgramAnalyzerResponseItem]]:
        return self._results

    @abstractmethod
    def parse_output_line(self, line: str) -> Optional[ProgramAnalyzerResponseItem]: ...

    def start_subprocess(self, main_file: str) -> None:
        cmd = self.get_command_line(main_file)
        logger.info("Starting subprocess %r in %r", cmd, get_workbench().get_local_cwd())
        logger.info("Cmd: %s", shlex.join(cmd))
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=get_workbench().get_local_cwd(),
        )

    def cancel(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.kill()
            except Exception:
                logger.warning("Could not kill subprocess in %r", type(self))
            finally:
                self._proc = None
                self._results = None

    @abstractmethod
    def get_command_line(self, main_file_path: str) -> List[str]: ...

    def get_env(self) -> Dict[str, str]:
        return {}
