from exa.chat_pb import chat_pb2 as _chat_pb2
from exa.codeium_common_pb import codeium_common_pb2 as _codeium_common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CodeiumState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CODEIUM_STATE_UNSPECIFIED: _ClassVar[CodeiumState]
    CODEIUM_STATE_INACTIVE: _ClassVar[CodeiumState]
    CODEIUM_STATE_PROCESSING: _ClassVar[CodeiumState]
    CODEIUM_STATE_SUCCESS: _ClassVar[CodeiumState]
    CODEIUM_STATE_WARNING: _ClassVar[CodeiumState]
    CODEIUM_STATE_ERROR: _ClassVar[CodeiumState]

class LineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LINE_TYPE_UNSPECIFIED: _ClassVar[LineType]
    LINE_TYPE_SINGLE: _ClassVar[LineType]
    LINE_TYPE_MULTI: _ClassVar[LineType]

class CompletionPartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPLETION_PART_TYPE_UNSPECIFIED: _ClassVar[CompletionPartType]
    COMPLETION_PART_TYPE_INLINE: _ClassVar[CompletionPartType]
    COMPLETION_PART_TYPE_BLOCK: _ClassVar[CompletionPartType]
    COMPLETION_PART_TYPE_INLINE_MASK: _ClassVar[CompletionPartType]
CODEIUM_STATE_UNSPECIFIED: CodeiumState
CODEIUM_STATE_INACTIVE: CodeiumState
CODEIUM_STATE_PROCESSING: CodeiumState
CODEIUM_STATE_SUCCESS: CodeiumState
CODEIUM_STATE_WARNING: CodeiumState
CODEIUM_STATE_ERROR: CodeiumState
LINE_TYPE_UNSPECIFIED: LineType
LINE_TYPE_SINGLE: LineType
LINE_TYPE_MULTI: LineType
COMPLETION_PART_TYPE_UNSPECIFIED: CompletionPartType
COMPLETION_PART_TYPE_INLINE: CompletionPartType
COMPLETION_PART_TYPE_BLOCK: CompletionPartType
COMPLETION_PART_TYPE_INLINE_MASK: CompletionPartType

class GetCompletionsRequest(_message.Message):
    __slots__ = ("metadata", "document", "editor_options", "other_documents", "model_name")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    EDITOR_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    OTHER_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    document: Document
    editor_options: _codeium_common_pb2.EditorOptions
    other_documents: _containers.RepeatedCompositeFieldContainer[Document]
    model_name: str
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., document: _Optional[_Union[Document, _Mapping]] = ..., editor_options: _Optional[_Union[_codeium_common_pb2.EditorOptions, _Mapping]] = ..., other_documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ..., model_name: _Optional[str] = ...) -> None: ...

class GetCompletionsResponse(_message.Message):
    __slots__ = ("state", "completion_items")
    STATE_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_ITEMS_FIELD_NUMBER: _ClassVar[int]
    state: State
    completion_items: _containers.RepeatedCompositeFieldContainer[CompletionItem]
    def __init__(self, state: _Optional[_Union[State, _Mapping]] = ..., completion_items: _Optional[_Iterable[_Union[CompletionItem, _Mapping]]] = ...) -> None: ...

class AcceptCompletionRequest(_message.Message):
    __slots__ = ("metadata", "completion_id")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    completion_id: str
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., completion_id: _Optional[str] = ...) -> None: ...

class AcceptCompletionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("metadata",)
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAuthTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAuthTokenResponse(_message.Message):
    __slots__ = ("auth_token", "uuid")
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    uuid: str
    def __init__(self, auth_token: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class RecordEventRequest(_message.Message):
    __slots__ = ("metadata", "event")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    event: _codeium_common_pb2.Event
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., event: _Optional[_Union[_codeium_common_pb2.Event, _Mapping]] = ...) -> None: ...

class RecordEventResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CancelRequestRequest(_message.Message):
    __slots__ = ("metadata", "request_id")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    request_id: int
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., request_id: _Optional[int] = ...) -> None: ...

class CancelRequestResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExitResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProcessesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProcessesResponse(_message.Message):
    __slots__ = ("lsp_port", "chat_web_server_port", "chat_client_port")
    LSP_PORT_FIELD_NUMBER: _ClassVar[int]
    CHAT_WEB_SERVER_PORT_FIELD_NUMBER: _ClassVar[int]
    CHAT_CLIENT_PORT_FIELD_NUMBER: _ClassVar[int]
    lsp_port: int
    chat_web_server_port: int
    chat_client_port: int
    def __init__(self, lsp_port: _Optional[int] = ..., chat_web_server_port: _Optional[int] = ..., chat_client_port: _Optional[int] = ...) -> None: ...

class GetChatMessageRequest(_message.Message):
    __slots__ = ("metadata", "prompt", "chat_messages", "experiment_config", "active_document", "open_document_paths", "workspace_paths", "context_inclusion_type")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    CHAT_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    OPEN_DOCUMENT_PATHS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_PATHS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_INCLUSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    prompt: str
    chat_messages: _containers.RepeatedCompositeFieldContainer[_chat_pb2.ChatMessage]
    experiment_config: ExperimentConfig
    active_document: Document
    open_document_paths: _containers.RepeatedScalarFieldContainer[str]
    workspace_paths: _containers.RepeatedScalarFieldContainer[str]
    context_inclusion_type: _codeium_common_pb2.ContextInclusionType
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., prompt: _Optional[str] = ..., chat_messages: _Optional[_Iterable[_Union[_chat_pb2.ChatMessage, _Mapping]]] = ..., experiment_config: _Optional[_Union[ExperimentConfig, _Mapping]] = ..., active_document: _Optional[_Union[Document, _Mapping]] = ..., open_document_paths: _Optional[_Iterable[str]] = ..., workspace_paths: _Optional[_Iterable[str]] = ..., context_inclusion_type: _Optional[_Union[_codeium_common_pb2.ContextInclusionType, str]] = ...) -> None: ...

class GetChatMessageResponse(_message.Message):
    __slots__ = ("chat_message",)
    CHAT_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    chat_message: _chat_pb2.ChatMessage
    def __init__(self, chat_message: _Optional[_Union[_chat_pb2.ChatMessage, _Mapping]] = ...) -> None: ...

class RecordChatFeedbackRequest(_message.Message):
    __slots__ = ("metadata", "message_id", "feedback", "reason", "timestamp")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    message_id: str
    feedback: _chat_pb2.ChatFeedbackType
    reason: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., message_id: _Optional[str] = ..., feedback: _Optional[_Union[_chat_pb2.ChatFeedbackType, str]] = ..., reason: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RecordChatFeedbackResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RecordChatPanelSessionRequest(_message.Message):
    __slots__ = ("metadata", "start_timestamp", "end_timestamp")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RecordChatPanelSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClusteredSearchRequest(_message.Message):
    __slots__ = ("metadata", "query", "num_results", "num_clusters")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    NUM_RESULTS_FIELD_NUMBER: _ClassVar[int]
    NUM_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    query: str
    num_results: int
    num_clusters: int
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., query: _Optional[str] = ..., num_results: _Optional[int] = ..., num_clusters: _Optional[int] = ...) -> None: ...

class ClusteredSearchResponse(_message.Message):
    __slots__ = ("clusters", "search_id")
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ID_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[SearchResultCluster]
    search_id: str
    def __init__(self, clusters: _Optional[_Iterable[_Union[SearchResultCluster, _Mapping]]] = ..., search_id: _Optional[str] = ...) -> None: ...

class ExactSearchRequest(_message.Message):
    __slots__ = ("metadata", "query", "options")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    query: ExactSearchQuery
    options: ExactSearchOptions
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ..., query: _Optional[_Union[ExactSearchQuery, _Mapping]] = ..., options: _Optional[_Union[ExactSearchOptions, _Mapping]] = ...) -> None: ...

class ExactSearchResponse(_message.Message):
    __slots__ = ("results", "hit_limit", "search_id")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    HIT_LIMIT_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ID_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ExactSearchResult]
    hit_limit: bool
    search_id: str
    def __init__(self, results: _Optional[_Iterable[_Union[ExactSearchResult, _Mapping]]] = ..., hit_limit: bool = ..., search_id: _Optional[str] = ...) -> None: ...

class AddTrackedWorkspaceRequest(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class AddTrackedWorkspaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveTrackedWorkspaceRequest(_message.Message):
    __slots__ = ("workspace",)
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class RemoveTrackedWorkspaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RefreshContextForIdeActionRequest(_message.Message):
    __slots__ = ("active_document", "open_document_filepaths", "workspace_paths", "blocking")
    ACTIVE_DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    OPEN_DOCUMENT_FILEPATHS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_PATHS_FIELD_NUMBER: _ClassVar[int]
    BLOCKING_FIELD_NUMBER: _ClassVar[int]
    active_document: Document
    open_document_filepaths: _containers.RepeatedScalarFieldContainer[str]
    workspace_paths: _containers.RepeatedScalarFieldContainer[str]
    blocking: bool
    def __init__(self, active_document: _Optional[_Union[Document, _Mapping]] = ..., open_document_filepaths: _Optional[_Iterable[str]] = ..., workspace_paths: _Optional[_Iterable[str]] = ..., blocking: bool = ...) -> None: ...

class RefreshContextForIdeActionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetFunctionsRequest(_message.Message):
    __slots__ = ("document",)
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    document: Document
    def __init__(self, document: _Optional[_Union[Document, _Mapping]] = ...) -> None: ...

class GetFunctionsResponse(_message.Message):
    __slots__ = ("function_captures",)
    FUNCTION_CAPTURES_FIELD_NUMBER: _ClassVar[int]
    function_captures: _containers.RepeatedCompositeFieldContainer[_codeium_common_pb2.FunctionInfo]
    def __init__(self, function_captures: _Optional[_Iterable[_Union[_codeium_common_pb2.FunctionInfo, _Mapping]]] = ...) -> None: ...

class GetUserStatusRequest(_message.Message):
    __slots__ = ("metadata",)
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _codeium_common_pb2.Metadata
    def __init__(self, metadata: _Optional[_Union[_codeium_common_pb2.Metadata, _Mapping]] = ...) -> None: ...

class GetUserStatusResponse(_message.Message):
    __slots__ = ("user_status",)
    USER_STATUS_FIELD_NUMBER: _ClassVar[int]
    user_status: _codeium_common_pb2.UserStatus
    def __init__(self, user_status: _Optional[_Union[_codeium_common_pb2.UserStatus, _Mapping]] = ...) -> None: ...

class DocumentPosition(_message.Message):
    __slots__ = ("row", "col")
    ROW_FIELD_NUMBER: _ClassVar[int]
    COL_FIELD_NUMBER: _ClassVar[int]
    row: int
    col: int
    def __init__(self, row: _Optional[int] = ..., col: _Optional[int] = ...) -> None: ...

class Document(_message.Message):
    __slots__ = ("absolute_path", "relative_path", "text", "editor_language", "language", "cursor_offset", "cursor_position", "line_ending", "visible_range")
    ABSOLUTE_PATH_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EDITOR_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_OFFSET_FIELD_NUMBER: _ClassVar[int]
    CURSOR_POSITION_FIELD_NUMBER: _ClassVar[int]
    LINE_ENDING_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_RANGE_FIELD_NUMBER: _ClassVar[int]
    absolute_path: str
    relative_path: str
    text: str
    editor_language: str
    language: _codeium_common_pb2.Language
    cursor_offset: int
    cursor_position: DocumentPosition
    line_ending: str
    visible_range: Range
    def __init__(self, absolute_path: _Optional[str] = ..., relative_path: _Optional[str] = ..., text: _Optional[str] = ..., editor_language: _Optional[str] = ..., language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., cursor_offset: _Optional[int] = ..., cursor_position: _Optional[_Union[DocumentPosition, _Mapping]] = ..., line_ending: _Optional[str] = ..., visible_range: _Optional[_Union[Range, _Mapping]] = ...) -> None: ...

class EditorOptions(_message.Message):
    __slots__ = ("tab_size", "insert_spaces")
    TAB_SIZE_FIELD_NUMBER: _ClassVar[int]
    INSERT_SPACES_FIELD_NUMBER: _ClassVar[int]
    tab_size: int
    insert_spaces: bool
    def __init__(self, tab_size: _Optional[int] = ..., insert_spaces: bool = ...) -> None: ...

class State(_message.Message):
    __slots__ = ("state", "message")
    STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: CodeiumState
    message: str
    def __init__(self, state: _Optional[_Union[CodeiumState, str]] = ..., message: _Optional[str] = ...) -> None: ...

class Range(_message.Message):
    __slots__ = ("start_offset", "end_offset", "start_position", "end_position")
    START_OFFSET_FIELD_NUMBER: _ClassVar[int]
    END_OFFSET_FIELD_NUMBER: _ClassVar[int]
    START_POSITION_FIELD_NUMBER: _ClassVar[int]
    END_POSITION_FIELD_NUMBER: _ClassVar[int]
    start_offset: int
    end_offset: int
    start_position: DocumentPosition
    end_position: DocumentPosition
    def __init__(self, start_offset: _Optional[int] = ..., end_offset: _Optional[int] = ..., start_position: _Optional[_Union[DocumentPosition, _Mapping]] = ..., end_position: _Optional[_Union[DocumentPosition, _Mapping]] = ...) -> None: ...

class Suffix(_message.Message):
    __slots__ = ("text", "delta_cursor_offset")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DELTA_CURSOR_OFFSET_FIELD_NUMBER: _ClassVar[int]
    text: str
    delta_cursor_offset: int
    def __init__(self, text: _Optional[str] = ..., delta_cursor_offset: _Optional[int] = ...) -> None: ...

class CompletionPart(_message.Message):
    __slots__ = ("text", "offset", "type", "prefix", "line")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    text: str
    offset: int
    type: CompletionPartType
    prefix: str
    line: int
    def __init__(self, text: _Optional[str] = ..., offset: _Optional[int] = ..., type: _Optional[_Union[CompletionPartType, str]] = ..., prefix: _Optional[str] = ..., line: _Optional[int] = ...) -> None: ...

class CompletionItem(_message.Message):
    __slots__ = ("completion", "suffix", "range", "source", "completion_parts")
    COMPLETION_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_PARTS_FIELD_NUMBER: _ClassVar[int]
    completion: _codeium_common_pb2.Completion
    suffix: Suffix
    range: Range
    source: _codeium_common_pb2.CompletionSource
    completion_parts: _containers.RepeatedCompositeFieldContainer[CompletionPart]
    def __init__(self, completion: _Optional[_Union[_codeium_common_pb2.Completion, _Mapping]] = ..., suffix: _Optional[_Union[Suffix, _Mapping]] = ..., range: _Optional[_Union[Range, _Mapping]] = ..., source: _Optional[_Union[_codeium_common_pb2.CompletionSource, str]] = ..., completion_parts: _Optional[_Iterable[_Union[CompletionPart, _Mapping]]] = ...) -> None: ...

class ExperimentConfig(_message.Message):
    __slots__ = ("force_enable_experiments", "force_disable_experiments")
    FORCE_ENABLE_EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
    FORCE_DISABLE_EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
    force_enable_experiments: _containers.RepeatedScalarFieldContainer[_codeium_common_pb2.ExperimentKey]
    force_disable_experiments: _containers.RepeatedScalarFieldContainer[_codeium_common_pb2.ExperimentKey]
    def __init__(self, force_enable_experiments: _Optional[_Iterable[_Union[_codeium_common_pb2.ExperimentKey, str]]] = ..., force_disable_experiments: _Optional[_Iterable[_Union[_codeium_common_pb2.ExperimentKey, str]]] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ("embedding_id", "absolute_path", "workspace_paths", "embedding_metadata", "similarity_score", "code_context_item")
    EMBEDDING_ID_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_PATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_PATHS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_METADATA_FIELD_NUMBER: _ClassVar[int]
    SIMILARITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    CODE_CONTEXT_ITEM_FIELD_NUMBER: _ClassVar[int]
    embedding_id: int
    absolute_path: str
    workspace_paths: _containers.RepeatedCompositeFieldContainer[_codeium_common_pb2.WorkspacePath]
    embedding_metadata: _codeium_common_pb2.EmbeddingMetadata
    similarity_score: float
    code_context_item: _codeium_common_pb2.CodeContextItem
    def __init__(self, embedding_id: _Optional[int] = ..., absolute_path: _Optional[str] = ..., workspace_paths: _Optional[_Iterable[_Union[_codeium_common_pb2.WorkspacePath, _Mapping]]] = ..., embedding_metadata: _Optional[_Union[_codeium_common_pb2.EmbeddingMetadata, _Mapping]] = ..., similarity_score: _Optional[float] = ..., code_context_item: _Optional[_Union[_codeium_common_pb2.CodeContextItem, _Mapping]] = ...) -> None: ...

class SearchResultCluster(_message.Message):
    __slots__ = ("search_results", "representative_path", "description", "mean_similarity_score", "search_id", "result_id")
    SEARCH_RESULTS_FIELD_NUMBER: _ClassVar[int]
    REPRESENTATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MEAN_SIMILARITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    search_results: _containers.RepeatedCompositeFieldContainer[SearchResult]
    representative_path: str
    description: str
    mean_similarity_score: float
    search_id: str
    result_id: str
    def __init__(self, search_results: _Optional[_Iterable[_Union[SearchResult, _Mapping]]] = ..., representative_path: _Optional[str] = ..., description: _Optional[str] = ..., mean_similarity_score: _Optional[float] = ..., search_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...

class ProgressBar(_message.Message):
    __slots__ = ("progress", "text", "hidden")
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_FIELD_NUMBER: _ClassVar[int]
    progress: float
    text: str
    hidden: bool
    def __init__(self, progress: _Optional[float] = ..., text: _Optional[str] = ..., hidden: bool = ...) -> None: ...

class ExactSearchQuery(_message.Message):
    __slots__ = ("pattern", "is_multiline", "is_reg_exp", "is_case_sensitive", "is_word_match")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    IS_MULTILINE_FIELD_NUMBER: _ClassVar[int]
    IS_REG_EXP_FIELD_NUMBER: _ClassVar[int]
    IS_CASE_SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    IS_WORD_MATCH_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    is_multiline: bool
    is_reg_exp: bool
    is_case_sensitive: bool
    is_word_match: bool
    def __init__(self, pattern: _Optional[str] = ..., is_multiline: bool = ..., is_reg_exp: bool = ..., is_case_sensitive: bool = ..., is_word_match: bool = ...) -> None: ...

class ExactSearchOptions(_message.Message):
    __slots__ = ("folder", "includes", "excludes", "disregard_ignore_files", "follow_symlinks", "disregard_global_ignore_files", "disregard_parent_ignore_files", "max_file_size", "encoding", "before_context_lines", "after_context_lines", "max_results", "preview_options")
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    INCLUDES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    DISREGARD_IGNORE_FILES_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_SYMLINKS_FIELD_NUMBER: _ClassVar[int]
    DISREGARD_GLOBAL_IGNORE_FILES_FIELD_NUMBER: _ClassVar[int]
    DISREGARD_PARENT_IGNORE_FILES_FIELD_NUMBER: _ClassVar[int]
    MAX_FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    BEFORE_CONTEXT_LINES_FIELD_NUMBER: _ClassVar[int]
    AFTER_CONTEXT_LINES_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    folder: str
    includes: _containers.RepeatedScalarFieldContainer[str]
    excludes: _containers.RepeatedScalarFieldContainer[str]
    disregard_ignore_files: bool
    follow_symlinks: bool
    disregard_global_ignore_files: bool
    disregard_parent_ignore_files: bool
    max_file_size: int
    encoding: str
    before_context_lines: int
    after_context_lines: int
    max_results: int
    preview_options: ExactSearchPreviewOptions
    def __init__(self, folder: _Optional[str] = ..., includes: _Optional[_Iterable[str]] = ..., excludes: _Optional[_Iterable[str]] = ..., disregard_ignore_files: bool = ..., follow_symlinks: bool = ..., disregard_global_ignore_files: bool = ..., disregard_parent_ignore_files: bool = ..., max_file_size: _Optional[int] = ..., encoding: _Optional[str] = ..., before_context_lines: _Optional[int] = ..., after_context_lines: _Optional[int] = ..., max_results: _Optional[int] = ..., preview_options: _Optional[_Union[ExactSearchPreviewOptions, _Mapping]] = ...) -> None: ...

class ExactSearchPreviewOptions(_message.Message):
    __slots__ = ("match_lines", "chars_per_line")
    MATCH_LINES_FIELD_NUMBER: _ClassVar[int]
    CHARS_PER_LINE_FIELD_NUMBER: _ClassVar[int]
    match_lines: int
    chars_per_line: int
    def __init__(self, match_lines: _Optional[int] = ..., chars_per_line: _Optional[int] = ...) -> None: ...

class ExactSearchResult(_message.Message):
    __slots__ = ("absolute_path", "relative_path", "ranges", "preview", "result_id")
    ABSOLUTE_PATH_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    RANGES_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    absolute_path: str
    relative_path: str
    ranges: _containers.RepeatedCompositeFieldContainer[Range]
    preview: ExactSearchMatchPreview
    result_id: str
    def __init__(self, absolute_path: _Optional[str] = ..., relative_path: _Optional[str] = ..., ranges: _Optional[_Iterable[_Union[Range, _Mapping]]] = ..., preview: _Optional[_Union[ExactSearchMatchPreview, _Mapping]] = ..., result_id: _Optional[str] = ...) -> None: ...

class ExactSearchMatchPreview(_message.Message):
    __slots__ = ("text", "ranges")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    RANGES_FIELD_NUMBER: _ClassVar[int]
    text: str
    ranges: _containers.RepeatedCompositeFieldContainer[Range]
    def __init__(self, text: _Optional[str] = ..., ranges: _Optional[_Iterable[_Union[Range, _Mapping]]] = ...) -> None: ...
