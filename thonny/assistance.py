import ast
import dataclasses
import datetime
import os.path
import re
import subprocess
import textwrap
import threading
import tkinter as tk
import uuid
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, replace
from enum import Enum
from logging import getLogger
from typing import Dict, Iterable, Iterator, List, cast
from typing import Optional
from typing import Tuple

from thonny import get_runner, get_workbench, rst_utils, tktextext, ui_utils
from thonny.common import (
    STRING_PSEUDO_FILENAME,
    ToplevelResponse,
    is_remote_path,
    read_source,
)
from thonny.languages import tr
from thonny.ui_utils import (
    ems_to_pixels,
    lookup_style_option,
    shift_is_pressed,
)

logger = getLogger(__name__)

Suggestion = namedtuple("Suggestion", ["symbol", "title", "body", "relevance"])

_last_feedback_timestamps = {}  # type: Dict[str, str]


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponseChunk:
    content: str
    is_final: bool
    is_interal_error: bool = False


@dataclass
class ChatResponseFragmentWithRequestId:
    fragment: ChatResponseChunk
    request_id: str


@dataclass
class ChatContext:
    messages: List[ChatMessage]
    main_file_path: Optional[str] = None
    imported_file_paths: List[str] = dataclasses.field(default_factory=list)
    active_file_path: Optional[str] = None
    active_file_selection: Optional[str] = None
    file_contents_by_path: Dict[str, str] = dataclasses.field(default=dict)
    execution_io: Optional[str] = None


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


class Assistant(ABC):
    @abstractmethod
    def get_ready(self) -> bool:
        """Called in the UI thread before each request"""
        ...

    @abstractmethod
    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        """Called in a background thread"""
        ...

    @abstractmethod
    def cancel_completion(self) -> None:
        """Called in the UI thread"""
        ...


class AssistantView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(
            self,
            master,
            text_class=AssistantRstText,
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            vertical_scrollbar_rowspan=2,
            read_only=True,
            wrap="word",
            font="TkDefaultFont",
            # cursor="arrow",
            padx=10,
            pady=0,
            insertwidth=0,
            background="white",
        )

        self._analyzer_instances = []

        self._chat_messages: List[ChatMessage] = []
        self._active_chat_request_id: Optional[str] = None

        self._snapshots_per_main_file = {}
        self._current_snapshot = None

        self._accepted_warning_sets = []

        self.text.tag_configure(
            "section_title",
            spacing3=5,
            font="BoldTkDefaultFont",
        )
        self.text.tag_configure(
            "intro",
            # font="ItalicTkDefaultFont",
            spacing3=10,
        )
        self.text.tag_configure("relevant_suggestion_title", font="BoldTkDefaultFont")
        self.text.tag_configure("suggestion_title", lmargin2=16, spacing1=5, spacing3=5)
        self.text.tag_configure("suggestion_body", lmargin1=16, lmargin2=16)
        self.text.tag_configure("body", font="ItalicTkDefaultFont")

        self._last_analysis_start_index = "1.0"
        self._last_analysis_end_index = "1.0"

        main_font = tk.font.nametofont("TkDefaultFont")

        # Underline on font looks better than underline on tag
        italic_underline_font = main_font.copy()
        italic_underline_font.configure(slant="italic", size=main_font.cget("size"), underline=True)

        self.text.tag_configure("feedback_link", justify="right", font=italic_underline_font)
        self.text.tag_configure("python_errors_link", justify="right", font=italic_underline_font)
        self.text.tag_bind(
            "python_errors_link",
            "<ButtonRelease-1>",
            lambda e: get_workbench().open_url("errors.rst"),
            True,
        )

        self.query_box = self.create_query_panel()
        self.query_box.grid(
            row=1, column=1, sticky="nsew", padx=ems_to_pixels(1), pady=ems_to_pixels(1)
        )

        from thonny.plugins.openai import OpenAIAssistant

        self._default_assistant: Assistant = OpenAIAssistant()  # TODO

        get_workbench().bind("ToplevelResponse", self.handle_toplevel_response, True)
        get_workbench().bind("AiChatResponseFragment", self.handle_assistant_chat_response_fragment, True)

        self.bind("<<ThemeChanged>>", self._on_theme_changed, True)

    def create_query_panel(self) -> tk.Frame:
        border_frame = tk.Frame(self, background="#cccccc")

        inside_frame = tk.Frame(border_frame, background="white")
        inside_frame.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        inside_frame.rowconfigure(0, weight=1)
        inside_frame.columnconfigure(0, weight=1)

        self.query_text = tk.Text(
            inside_frame,
            height=2,
            font="TkDefaultFont",
            borderwidth=0,
            highlightthickness=0,
            relief="groove",
            wrap="word",
        )
        self.query_text.bind("<Return>", self._on_press_enter_in_chat_entry, True)
        self.query_text.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        border_frame.rowconfigure(0, weight=1)
        border_frame.columnconfigure(0, weight=1)

        return border_frame

    def handle_assistant_chat_response_fragment(
        self, fragment_with_request_id: ChatResponseFragmentWithRequestId
    ) -> None:
        if fragment_with_request_id.request_id != self._active_chat_request_id:
            logger.info("Skipping chat fragment, because request has been cancelled")
            return

        fragment = fragment_with_request_id.fragment
        self._append_text(fragment.content, source="chat")
        last_msg = self._chat_messages.pop()
        if last_msg.role == "user":
            self._chat_messages.append(last_msg)
            current_msg = ChatMessage("assistant", "")
        else:
            current_msg = last_msg

        print("CURRR", fragment)
        current_msg = replace(current_msg, content=current_msg.content + fragment.content)
        self._chat_messages.append(current_msg)
        if fragment.is_final:
            self._append_text("\n------------\n", source="chat")
            self._active_chat_request_id = None

    def handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        from thonny.plugins.cpython_frontend import LocalCPythonProxy

        if not isinstance(get_runner().get_backend_proxy(), LocalCPythonProxy):
            # TODO: add some support for MicroPython as well
            return

        # Can be called by event system or by Workbench
        # (if Assistant wasn't created yet but an error came)
        if not msg.get("user_exception") and msg.get("command_name") in [
            "execute_system_command",
            "execute_source",
        ]:
            # Shell commands may be used to investigate the problem, don't clear assistance
            return

        self._prepare_new_analysis()

        # prepare for snapshot
        # TODO: should distinguish between <string> and <stdin> ?
        key = msg.get("filename", STRING_PSEUDO_FILENAME)
        self._current_snapshot = {
            "timestamp": datetime.datetime.now().isoformat()[:19],
            "main_file_path": key,
        }
        self._snapshots_per_main_file.setdefault(key, [])
        self._snapshots_per_main_file[key].append(self._current_snapshot)

        if msg.get("user_exception"):
            if not msg["user_exception"].get("message", None):
                msg["user_exception"]["message"] = "<no message>"

            self._exception_info = msg["user_exception"]
            self._explain_exception(msg["user_exception"])
            if get_workbench().get_option("assistance.open_assistant_on_errors"):
                get_workbench().show_view("AssistantView", set_focus=False)
        else:
            self._exception_info = None

        if msg.get("filename") and os.path.exists(msg["filename"]):
            self.main_file_path = msg["filename"]
            self.submit_user_chat_message("@pylint\n")
        else:
            self.main_file_path = None

    def _explain_exception(self, error_info):
        rst = (
            self._get_rst_prelude()
            + rst_utils.create_title(
                error_info["type_name"] + ": " + rst_utils.escape(error_info["message"])
            )
            + "\n"
        )

        if (
            error_info.get("lineno") is not None
            and error_info.get("filename")
            and os.path.exists(error_info["filename"])
        ):
            rst += "`%s, line %d <%s>`__\n\n" % (
                os.path.basename(error_info["filename"]),
                error_info["lineno"],
                self._format_file_url(error_info),
            )


    def _append_text(self, chars, tags=(), source="analysis"):
        self.text.direct_insert("end", chars, tags=tags)

        if source == "analysis":
            self._last_analysis_end_index = self.text.index("end")

    def _prepare_new_analysis(self):
        self._cancel_analysis()
        self._cancel_completion()

        text_after_last_analysis = self.text.get(self._last_analysis_end_index, "end")
        if not text_after_last_analysis.strip():
            # No question was asked after the last analysis, let's forget that analysis.
            self.text.direct_delete(self._last_analysis_start_index, "end-1c")

        self._last_analysis_start_index = self.text.index("end-1c")
        self._last_analysis_end_index = self.text.index("end-1c")

    def _prepare_new_completion(self):
        self._cancel_analysis()
        self._cancel_completion()

    def _cancel_analysis(self):
        if self._analysis_in_progress():
            self._accepted_warning_sets.clear()
            for wp in self._analyzer_instances:
                wp.cancel_analysis()
            self._analyzer_instances = []

    def _cancel_completion(self):
        if self._default_assistant is None:
            return

        if self._chat_completion_in_progress():
            self._active_chat_request_id = None
            self._append_text("... [cancelled]", source="chat")

            self._default_assistant.cancel_completion()

    def _analysis_in_progress(self) -> bool:
        return len(self._analyzer_instances) > 0

    def _chat_completion_in_progress(self) -> bool:
        return self._active_chat_request_id is not None

    def _format_file_url(self, atts):
        return format_file_url(atts["filename"], atts.get("lineno"), atts.get("col_offset"))

    def _get_rst_prelude(self):
        return ".. default-role:: code\n\n" + ".. role:: light\n\n" + ".. role:: remark\n\n"

    def _on_theme_changed(self, event):
        self.text.configure(
            background=lookup_style_option("Text", "background"),
            foreground=lookup_style_option("Text", "foreground"),
        )

        if isinstance(self.text, rst_utils.RstText):
            self.text.on_theme_changed()

    def _on_press_enter_in_chat_entry(self, event: tk.Event):
        if shift_is_pressed(event):
            return None

        if self._default_assistant.get_ready():
            self.submit_user_chat_message(self.query_text.get("1.0", "end"))

        return "break"

    def submit_user_chat_message(self, message: str):
        self._prepare_new_completion()

        self._active_chat_request_id = str(uuid.uuid4())
        self._append_text("\nYOU: " + message)
        self._chat_messages.append(ChatMessage("user", message))
        self.query_text.delete("1.0", "end")

        for assistant in self.select_assistants_for_user_message(message):
            threading.Thread(
                target=self._complete_chat_in_thread,
                daemon=True,
                args=(
                    assistant,
                    self._active_chat_request_id,
                ),
            ).start()

        return "break"

    def select_assistants_for_user_message(self, message: str) -> List[Assistant]:
        names = re.findall(r'@(\w+)', message)
        if not names:
            return [self._default_assistant]

        unique_norm_names = list(set(map(lambda s: s.lower(), names)))
        result = []
        for name in unique_norm_names:
            if name in get_workbench().assistants:
                result.append(get_workbench().assistants[name])

            else:
                # TODO:
                self._append_text(f"No assistant named {name}")

        return result

    def _complete_chat_in_thread(self, assistant: Assistant, request_id: str):
        try:
            # TODO: pass editor contents from UI thread
            main_file_path = _get_main_file()
            context = ChatContext(
                messages=self._chat_messages,
                main_file_path=main_file_path,
                imported_file_paths=_get_imported_user_files(main_file=main_file_path),
            )
            for fragment in assistant.complete_chat(context):
                get_workbench().queue_event(
                    "AiChatResponseFragment",
                    ChatResponseFragmentWithRequestId(fragment, request_id=request_id),
                )

                if fragment.is_final:
                    logger.debug("Finishing chat completion thread after final fragment")
                    break
        except Exception as e:
            logger.exception("Error when completing chat in thread")

            get_workbench().queue_event(
                "AiChatResponseFragment",
                ChatResponseFragmentWithRequestId(
                    ChatResponseChunk(
                        content=f"INTERNAL ERROR: {e}. See frontend.log for more details.",
                        is_final=True,
                    ),
                    request_id=request_id,
                ),
            )


class AssistantRstText(rst_utils.RstText):
    def configure_tags(self):
        super().configure_tags()

        main_font = tk.font.nametofont("TkDefaultFont")

        italic_font = main_font.copy()
        italic_font.configure(slant="italic", size=main_font.cget("size"))

        h1_font = main_font.copy()
        h1_font.configure(weight="bold", size=main_font.cget("size"))

        self.tag_configure("h1", font=h1_font, spacing3=0, spacing1=10)
        self.tag_configure("topic_title", font="TkDefaultFont")

        self.tag_configure("topic_body", font=italic_font, spacing1=10, lmargin1=25, lmargin2=25)

        self.tag_raise("sel")


class Helper:
    def get_intro(self) -> Tuple[str, int]:
        raise NotImplementedError()

    def get_suggestions(self) -> Iterable[Suggestion]:
        raise NotImplementedError()


class ErrorHelper(Helper):
    def __init__(self, error_info):
        # TODO: don't repeat all this for all error helpers
        self.error_info = error_info

        self.last_frame = error_info["stack"][-1]
        self.last_frame_ast = None
        if self.last_frame.source:
            try:
                self.last_frame_ast = ast.parse(self.last_frame.source, self.last_frame.filename)
            except SyntaxError:
                pass

        self.last_frame_module_source = None
        self.last_frame_module_ast = None
        if self.last_frame.code_name == "<module>":
            self.last_frame_module_source = self.last_frame.source
            self.last_frame_module_ast = self.last_frame_ast
        elif self.last_frame.filename is not None:
            try:
                self.last_frame_module_source = read_source(self.last_frame.filename)
                self.last_frame_module_ast = ast.parse(self.last_frame_module_source)
            except Exception:
                pass

        self.intro_confidence = 1
        self.intro_text = ""
        self.suggestions = []


class GenericErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        self.intro_text = "No specific suggestions for this error (yet)."
        self.intro_confidence = 1
        self.suggestions = []

        if error_info["message"].lower() != "invalid syntax":
            self.suggestions.append(
                Suggestion(
                    "generic-search-the-web",
                    "Search the web",
                    "Try performing a web search for\n\n``Python %s: %s``"
                    % (
                        self.error_info["type_name"],
                        rst_utils.escape(self.error_info["message"].replace("\n", " ").strip()),
                    ),
                    1,
                )
            )


class SubprocessProgramAnalyzer(Assistant, ABC):
    """
    Non-AI assistant, which can analyze program code
    """

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None

    def get_ready(self) -> bool:
        return True

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        main_file = _get_main_file()
        if main_file is None:
            yield ChatResponseChunk(content="I can only work with saved local files", is_final=True)
            return

        self.start_subprocess(context)
        for line in self._proc.stdout:
            item = self.parse_output_line(line, context)
            if item is not None:
                formatted_item = self.format_item(item)
                yield ChatResponseChunk(content=formatted_item + "\n", is_final=False)

        err = cast(str, self._proc.stderr.read().strip())
        if err:
            # TODO: use better format
            yield ChatResponseChunk(content="STDERR: " + err, is_final=False, is_interal_error=False)
        yield ChatResponseChunk(content="", is_final=True)

    def format_item(self, item: ProgramAnalyzerResponseItem) -> str:
        return "* " + item.message + " on line " + str(item.line)

    @abstractmethod
    def parse_output_line(
        self, line: str, context: ChatContext
    ) -> Optional[ProgramAnalyzerResponseItem]: ...

    def start_subprocess(self, context: ChatContext):
        cmd = self.get_command_line(context)
        logger.info("Starting subprocess %r", cmd)
        self._proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    def cancel_completion(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.kill()
            except Exception:
                logger.warning("Could not kill subprocess in %r", type(self))

    @abstractmethod
    def get_command_line(self, context: ChatContext) -> List[str]: ...

    def get_env(self) -> Dict[str, str]:
        return {}


class LibraryErrorHelper(ErrorHelper):
    """Explains exceptions, which doesn't happen in user code"""

    def get_intro(self):
        return "This error happened in library code. This may mean a bug in "

    def get_suggestions(self):
        return []




def _get_main_file() -> Optional[str]:
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if editor is None:
        return None

    filename = editor.get_filename()
    if filename is None or is_remote_path(filename):
        return None

    return filename


def _get_imported_user_files(main_file, source=None) -> List[str]:
    assert os.path.isabs(main_file)

    if source is None:
        source = read_source(main_file)

    try:
        root = ast.parse(source, main_file)
    except SyntaxError:
        return []

    main_dir = os.path.dirname(main_file)
    module_names = set()
    # TODO: at the moment only considers non-package modules
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for item in node.names:
                module_names.add(item.name)
        elif isinstance(node, ast.ImportFrom):
            module_names.add(node.module)

    imported_files = []

    for file in {
        name + ext for ext in [".py", ".pyw"] for name in module_names if name is not None
    }:
        possible_path = os.path.join(main_dir, file)
        if os.path.exists(possible_path):
            imported_files.append(possible_path)

    return imported_files
    # TODO: add recursion


def format_file_url(filename, lineno, col_offset):
    s = "thonny-editor://" + rst_utils.escape(filename).replace(" ", "%20")
    if lineno is not None:
        s += "#" + str(lineno)
        if col_offset is not None:
            s += ":" + str(col_offset)

    return s


def init():
    get_workbench().set_default("assistance.open_assistant_on_errors", True)
    get_workbench().set_default("assistance.open_assistant_on_warnings", False)
    get_workbench().set_default("assistance.disabled_checks", [])
    get_workbench().add_view(AssistantView, tr("Assistant"), "se", visible_by_default=False)
