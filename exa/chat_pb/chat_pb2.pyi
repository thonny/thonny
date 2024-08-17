from exa.codeium_common_pb import codeium_common_pb2 as _codeium_common_pb2
from exa.diff_action_pb import diff_action_pb2 as _diff_action_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatFeedbackType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEEDBACK_TYPE_UNSPECIFIED: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_ACCEPT: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_REJECT: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_COPIED: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_ACCEPT_DIFF: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_REJECT_DIFF: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_APPLY_DIFF: _ClassVar[ChatFeedbackType]
    FEEDBACK_TYPE_INSERT_AT_CURSOR: _ClassVar[ChatFeedbackType]
FEEDBACK_TYPE_UNSPECIFIED: ChatFeedbackType
FEEDBACK_TYPE_ACCEPT: ChatFeedbackType
FEEDBACK_TYPE_REJECT: ChatFeedbackType
FEEDBACK_TYPE_COPIED: ChatFeedbackType
FEEDBACK_TYPE_ACCEPT_DIFF: ChatFeedbackType
FEEDBACK_TYPE_REJECT_DIFF: ChatFeedbackType
FEEDBACK_TYPE_APPLY_DIFF: ChatFeedbackType
FEEDBACK_TYPE_INSERT_AT_CURSOR: ChatFeedbackType

class CodeBlockInfo(_message.Message):
    __slots__ = ("raw_source", "start_line", "start_col", "end_line", "end_col")
    RAW_SOURCE_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    START_COL_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    END_COL_FIELD_NUMBER: _ClassVar[int]
    raw_source: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    def __init__(self, raw_source: _Optional[str] = ..., start_line: _Optional[int] = ..., start_col: _Optional[int] = ..., end_line: _Optional[int] = ..., end_col: _Optional[int] = ...) -> None: ...

class IntentGeneric(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class IntentFunctionExplain(_message.Message):
    __slots__ = ("function_info", "language", "file_path")
    FUNCTION_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    function_info: _codeium_common_pb2.FunctionInfo
    language: _codeium_common_pb2.Language
    file_path: str
    def __init__(self, function_info: _Optional[_Union[_codeium_common_pb2.FunctionInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ...) -> None: ...

class IntentFunctionRefactor(_message.Message):
    __slots__ = ("function_info", "language", "file_path", "refactor_description")
    FUNCTION_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    REFACTOR_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    function_info: _codeium_common_pb2.FunctionInfo
    language: _codeium_common_pb2.Language
    file_path: str
    refactor_description: str
    def __init__(self, function_info: _Optional[_Union[_codeium_common_pb2.FunctionInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ..., refactor_description: _Optional[str] = ...) -> None: ...

class IntentFunctionUnitTests(_message.Message):
    __slots__ = ("function_info", "language", "file_path", "instructions")
    FUNCTION_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    function_info: _codeium_common_pb2.FunctionInfo
    language: _codeium_common_pb2.Language
    file_path: str
    instructions: str
    def __init__(self, function_info: _Optional[_Union[_codeium_common_pb2.FunctionInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ..., instructions: _Optional[str] = ...) -> None: ...

class IntentFunctionDocstring(_message.Message):
    __slots__ = ("function_info", "language", "file_path")
    FUNCTION_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    function_info: _codeium_common_pb2.FunctionInfo
    language: _codeium_common_pb2.Language
    file_path: str
    def __init__(self, function_info: _Optional[_Union[_codeium_common_pb2.FunctionInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ...) -> None: ...

class IntentCodeBlockExplain(_message.Message):
    __slots__ = ("code_block_info", "language", "file_path")
    CODE_BLOCK_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    code_block_info: CodeBlockInfo
    language: _codeium_common_pb2.Language
    file_path: str
    def __init__(self, code_block_info: _Optional[_Union[CodeBlockInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ...) -> None: ...

class IntentCodeBlockRefactor(_message.Message):
    __slots__ = ("code_block_info", "language", "file_path", "refactor_description")
    CODE_BLOCK_INFO_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    REFACTOR_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    code_block_info: CodeBlockInfo
    language: _codeium_common_pb2.Language
    file_path: str
    refactor_description: str
    def __init__(self, code_block_info: _Optional[_Union[CodeBlockInfo, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ..., refactor_description: _Optional[str] = ...) -> None: ...

class IntentProblemExplain(_message.Message):
    __slots__ = ("diagnostic_message", "problematic_code", "surrounding_code_snippet", "language", "file_path", "line_number")
    DIAGNOSTIC_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROBLEMATIC_CODE_FIELD_NUMBER: _ClassVar[int]
    SURROUNDING_CODE_SNIPPET_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    diagnostic_message: str
    problematic_code: CodeBlockInfo
    surrounding_code_snippet: str
    language: _codeium_common_pb2.Language
    file_path: str
    line_number: int
    def __init__(self, diagnostic_message: _Optional[str] = ..., problematic_code: _Optional[_Union[CodeBlockInfo, _Mapping]] = ..., surrounding_code_snippet: _Optional[str] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ..., line_number: _Optional[int] = ...) -> None: ...

class IntentGenerateCode(_message.Message):
    __slots__ = ("instruction", "language", "file_path", "line_number")
    INSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    instruction: str
    language: _codeium_common_pb2.Language
    file_path: str
    line_number: int
    def __init__(self, instruction: _Optional[str] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., file_path: _Optional[str] = ..., line_number: _Optional[int] = ...) -> None: ...

class ChatMessageIntent(_message.Message):
    __slots__ = ("generic", "explain_function", "function_docstring", "function_refactor", "explain_code_block", "code_block_refactor", "function_unit_tests", "problem_explain", "generate_code")
    GENERIC_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_DOCSTRING_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_REFACTOR_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_CODE_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CODE_BLOCK_REFACTOR_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_UNIT_TESTS_FIELD_NUMBER: _ClassVar[int]
    PROBLEM_EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    GENERATE_CODE_FIELD_NUMBER: _ClassVar[int]
    generic: IntentGeneric
    explain_function: IntentFunctionExplain
    function_docstring: IntentFunctionDocstring
    function_refactor: IntentFunctionRefactor
    explain_code_block: IntentCodeBlockExplain
    code_block_refactor: IntentCodeBlockRefactor
    function_unit_tests: IntentFunctionUnitTests
    problem_explain: IntentProblemExplain
    generate_code: IntentGenerateCode
    def __init__(self, generic: _Optional[_Union[IntentGeneric, _Mapping]] = ..., explain_function: _Optional[_Union[IntentFunctionExplain, _Mapping]] = ..., function_docstring: _Optional[_Union[IntentFunctionDocstring, _Mapping]] = ..., function_refactor: _Optional[_Union[IntentFunctionRefactor, _Mapping]] = ..., explain_code_block: _Optional[_Union[IntentCodeBlockExplain, _Mapping]] = ..., code_block_refactor: _Optional[_Union[IntentCodeBlockRefactor, _Mapping]] = ..., function_unit_tests: _Optional[_Union[IntentFunctionUnitTests, _Mapping]] = ..., problem_explain: _Optional[_Union[IntentProblemExplain, _Mapping]] = ..., generate_code: _Optional[_Union[IntentGenerateCode, _Mapping]] = ...) -> None: ...

class ChatMessageActionEdit(_message.Message):
    __slots__ = ("file_path", "diff", "language", "text_pre", "text_post")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    DIFF_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_PRE_FIELD_NUMBER: _ClassVar[int]
    TEXT_POST_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    diff: _diff_action_pb2.DiffBlock
    language: _codeium_common_pb2.Language
    text_pre: str
    text_post: str
    def __init__(self, file_path: _Optional[str] = ..., diff: _Optional[_Union[_diff_action_pb2.DiffBlock, _Mapping]] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., text_pre: _Optional[str] = ..., text_post: _Optional[str] = ...) -> None: ...

class ChatMessageActionGeneric(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class ChatMessageStatusContextRelevancy(_message.Message):
    __slots__ = ("is_loading", "is_relevant", "query_suggestions")
    IS_LOADING_FIELD_NUMBER: _ClassVar[int]
    IS_RELEVANT_FIELD_NUMBER: _ClassVar[int]
    QUERY_SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    is_loading: bool
    is_relevant: bool
    query_suggestions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, is_loading: bool = ..., is_relevant: bool = ..., query_suggestions: _Optional[_Iterable[str]] = ...) -> None: ...

class ChatMessageStatus(_message.Message):
    __slots__ = ("context_relevancy",)
    CONTEXT_RELEVANCY_FIELD_NUMBER: _ClassVar[int]
    context_relevancy: ChatMessageStatusContextRelevancy
    def __init__(self, context_relevancy: _Optional[_Union[ChatMessageStatusContextRelevancy, _Mapping]] = ...) -> None: ...

class ChatMessageError(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class ChatMessageAction(_message.Message):
    __slots__ = ("generic", "edit", "num_tokens", "context_items")
    GENERIC_FIELD_NUMBER: _ClassVar[int]
    EDIT_FIELD_NUMBER: _ClassVar[int]
    NUM_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ITEMS_FIELD_NUMBER: _ClassVar[int]
    generic: ChatMessageActionGeneric
    edit: ChatMessageActionEdit
    num_tokens: int
    context_items: _containers.RepeatedCompositeFieldContainer[_codeium_common_pb2.CodeContextItem]
    def __init__(self, generic: _Optional[_Union[ChatMessageActionGeneric, _Mapping]] = ..., edit: _Optional[_Union[ChatMessageActionEdit, _Mapping]] = ..., num_tokens: _Optional[int] = ..., context_items: _Optional[_Iterable[_Union[_codeium_common_pb2.CodeContextItem, _Mapping]]] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("message_id", "source", "timestamp", "conversation_id", "intent", "action", "error", "status", "in_progress")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    source: _codeium_common_pb2.ChatMessageSource
    timestamp: _timestamp_pb2.Timestamp
    conversation_id: str
    intent: ChatMessageIntent
    action: ChatMessageAction
    error: ChatMessageError
    status: ChatMessageStatus
    in_progress: bool
    def __init__(self, message_id: _Optional[str] = ..., source: _Optional[_Union[_codeium_common_pb2.ChatMessageSource, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., conversation_id: _Optional[str] = ..., intent: _Optional[_Union[ChatMessageIntent, _Mapping]] = ..., action: _Optional[_Union[ChatMessageAction, _Mapping]] = ..., error: _Optional[_Union[ChatMessageError, _Mapping]] = ..., status: _Optional[_Union[ChatMessageStatus, _Mapping]] = ..., in_progress: bool = ...) -> None: ...
