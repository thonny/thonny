import ast
import dataclasses
import os.path
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from logging import getLogger
from typing import Dict, Iterator, List, Optional

from thonny import get_workbench, rst_utils
from thonny.common import read_source
from thonny.misc_utils import local_path_to_uri

logger = getLogger(__name__)

Suggestion = namedtuple("Suggestion", ["symbol", "title", "body", "relevance"])

_last_feedback_timestamps = {}  # type: Dict[str, str]


@dataclass
class Attachment:
    description: str
    tag: Optional[str]
    content: str


@dataclass
class ChatMessage:
    role: str
    content: str
    attachments: List[Attachment]


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
    active_file_path: Optional[str] = None
    active_file_selection: Optional[str] = None
    file_contents_by_path: Dict[str, str] = dataclasses.field(default=dict)
    execution_io: Optional[str] = None


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

    def format_message(self, message: ChatMessage) -> str:
        result = self.format_attachments(message.attachments)

        if result:
            result += "User message:\n"

        result += message.content

        return result

    def format_attachments(self, attachments: List[Attachment]) -> str:
        result = ""
        for attachment in attachments:
            result += self.format_attachment(attachment)
        return result

    def format_attachment(self, attachment: Attachment) -> str:
        result = f"{attachment.description}"
        if attachment.tag is not None:
            result += f" (#{attachment.tag})"

        result += f":\n```\n{attachment.content}\n```\n\n"

        return result


class EchoAssistant(Assistant):

    def get_ready(self) -> bool:
        return True

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        yield ChatResponseChunk(
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

""",
            is_final=False,
            is_interal_error=False,
        )

        yield ChatResponseChunk(
            self.format_message(context.messages[-1]), is_final=True, is_interal_error=False
        )

    def cancel_completion(self) -> None:
        pass


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
        name + ext for ext in [".py", ".pyw", "pyde"] for name in module_names if name is not None
    }:
        possible_path = os.path.join(main_dir, file)
        if os.path.exists(possible_path):
            imported_files.append(possible_path)

    return imported_files
    # TODO: add recursion


def format_file_url(filename, lineno, col_offset):
    s = local_path_to_uri(filename)
    if lineno is not None:
        s += "#" + str(lineno)
        if col_offset is not None:
            s += ":" + str(col_offset)

    return s


def init():
    get_workbench().set_default("assistance.open_assistant_on_errors", True)
    get_workbench().set_default("assistance.open_assistant_on_warnings", False)
    get_workbench().set_default("assistance.disabled_checks", [])
