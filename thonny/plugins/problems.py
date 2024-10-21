import os.path
import threading
from logging import getLogger
from typing import List

from thonny import get_workbench
from thonny.common import ToplevelResponse
from thonny.languages import tr
from thonny.program_analysis import ProgramAnalyzer, ProgramAnalyzerResponseItem
from thonny.tktextext import TextFrame

logger = getLogger(__name__)


class ProblemsView(TextFrame):
    def __init__(self, master):
        super().__init__(master, horizontal_scrollbar=False)
        self._analyzers: List[ProgramAnalyzer] = []

        get_workbench().bind("ToplevelResponse", self.handle_toplevel_response, True)

        get_workbench().bind("ProgramAnalysisCompleted", self.on_single_analysis_completed, True)

    def handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        if msg.get("filename") and os.path.exists(msg["filename"]):
            self.start_analyses(msg["filename"])

    def start_analyses(self, main_file_path: str) -> None:
        for analyzer in self._analyzers:
            analyzer.cancel()

        self._analyzers = [
            analyzer
            for name, analyzer in get_workbench().program_analyzers.items()
            if get_workbench().get_option(f"analysis.{name}.enabled")
        ]

        for analyzer in self._analyzers:
            threading.Thread(
                target=analyzer.analyze,
                daemon=True,
                args=(main_file_path,),
            ).start()

    def on_single_analysis_completed(self, msg) -> None:
        logger.info("Analysis completed for %r", msg)
        all_results = []
        for analyzer in self._analyzers:
            single_analyzer_results = analyzer.get_results()
            if single_analyzer_results is None:
                return
            else:
                all_results.extend(single_analyzer_results)

        self.display_results(all_results)

    def display_results(self, results: List[ProgramAnalyzerResponseItem]) -> None:
        self.text.direct_delete("1.0", "end")

        for item in results:
            self.text.direct_insert("end", "* " + item.message + "\n")


def load_plugin():
    get_workbench().add_view(
        ProblemsView, tr("Problems?"), default_location="s", visible_by_default=False
    )
