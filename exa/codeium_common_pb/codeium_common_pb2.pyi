from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_ENABLE_CODEIUM: _ClassVar[EventType]
    EVENT_TYPE_DISABLE_CODEIUM: _ClassVar[EventType]
    EVENT_TYPE_SHOW_PREVIOUS_COMPLETION: _ClassVar[EventType]
    EVENT_TYPE_SHOW_NEXT_COMPLETION: _ClassVar[EventType]

class CompletionSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPLETION_SOURCE_UNSPECIFIED: _ClassVar[CompletionSource]
    COMPLETION_SOURCE_TYPING_AS_SUGGESTED: _ClassVar[CompletionSource]
    COMPLETION_SOURCE_CACHE: _ClassVar[CompletionSource]
    COMPLETION_SOURCE_NETWORK: _ClassVar[CompletionSource]

class Language(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LANGUAGE_UNSPECIFIED: _ClassVar[Language]
    LANGUAGE_C: _ClassVar[Language]
    LANGUAGE_CLOJURE: _ClassVar[Language]
    LANGUAGE_COFFEESCRIPT: _ClassVar[Language]
    LANGUAGE_CPP: _ClassVar[Language]
    LANGUAGE_CSHARP: _ClassVar[Language]
    LANGUAGE_CSS: _ClassVar[Language]
    LANGUAGE_CUDACPP: _ClassVar[Language]
    LANGUAGE_DOCKERFILE: _ClassVar[Language]
    LANGUAGE_GO: _ClassVar[Language]
    LANGUAGE_GROOVY: _ClassVar[Language]
    LANGUAGE_HANDLEBARS: _ClassVar[Language]
    LANGUAGE_HASKELL: _ClassVar[Language]
    LANGUAGE_HCL: _ClassVar[Language]
    LANGUAGE_HTML: _ClassVar[Language]
    LANGUAGE_INI: _ClassVar[Language]
    LANGUAGE_JAVA: _ClassVar[Language]
    LANGUAGE_JAVASCRIPT: _ClassVar[Language]
    LANGUAGE_JSON: _ClassVar[Language]
    LANGUAGE_JULIA: _ClassVar[Language]
    LANGUAGE_KOTLIN: _ClassVar[Language]
    LANGUAGE_LATEX: _ClassVar[Language]
    LANGUAGE_LESS: _ClassVar[Language]
    LANGUAGE_LUA: _ClassVar[Language]
    LANGUAGE_MAKEFILE: _ClassVar[Language]
    LANGUAGE_MARKDOWN: _ClassVar[Language]
    LANGUAGE_OBJECTIVEC: _ClassVar[Language]
    LANGUAGE_OBJECTIVECPP: _ClassVar[Language]
    LANGUAGE_PERL: _ClassVar[Language]
    LANGUAGE_PHP: _ClassVar[Language]
    LANGUAGE_PLAINTEXT: _ClassVar[Language]
    LANGUAGE_PROTOBUF: _ClassVar[Language]
    LANGUAGE_PBTXT: _ClassVar[Language]
    LANGUAGE_PYTHON: _ClassVar[Language]
    LANGUAGE_R: _ClassVar[Language]
    LANGUAGE_RUBY: _ClassVar[Language]
    LANGUAGE_RUST: _ClassVar[Language]
    LANGUAGE_SASS: _ClassVar[Language]
    LANGUAGE_SCALA: _ClassVar[Language]
    LANGUAGE_SCSS: _ClassVar[Language]
    LANGUAGE_SHELL: _ClassVar[Language]
    LANGUAGE_SQL: _ClassVar[Language]
    LANGUAGE_STARLARK: _ClassVar[Language]
    LANGUAGE_SWIFT: _ClassVar[Language]
    LANGUAGE_TSX: _ClassVar[Language]
    LANGUAGE_TYPESCRIPT: _ClassVar[Language]
    LANGUAGE_VISUALBASIC: _ClassVar[Language]
    LANGUAGE_VUE: _ClassVar[Language]
    LANGUAGE_XML: _ClassVar[Language]
    LANGUAGE_XSL: _ClassVar[Language]
    LANGUAGE_YAML: _ClassVar[Language]
    LANGUAGE_SVELTE: _ClassVar[Language]
    LANGUAGE_TOML: _ClassVar[Language]
    LANGUAGE_DART: _ClassVar[Language]
    LANGUAGE_RST: _ClassVar[Language]
    LANGUAGE_OCAML: _ClassVar[Language]
    LANGUAGE_CMAKE: _ClassVar[Language]
    LANGUAGE_PASCAL: _ClassVar[Language]
    LANGUAGE_ELIXIR: _ClassVar[Language]
    LANGUAGE_FSHARP: _ClassVar[Language]
    LANGUAGE_LISP: _ClassVar[Language]
    LANGUAGE_MATLAB: _ClassVar[Language]
    LANGUAGE_POWERSHELL: _ClassVar[Language]
    LANGUAGE_SOLIDITY: _ClassVar[Language]
    LANGUAGE_ADA: _ClassVar[Language]
    LANGUAGE_OCAML_INTERFACE: _ClassVar[Language]
    LANGUAGE_TREE_SITTER_QUERY: _ClassVar[Language]
    LANGUAGE_APL: _ClassVar[Language]
    LANGUAGE_ASSEMBLY: _ClassVar[Language]
    LANGUAGE_COBOL: _ClassVar[Language]
    LANGUAGE_CRYSTAL: _ClassVar[Language]
    LANGUAGE_EMACS_LISP: _ClassVar[Language]
    LANGUAGE_ERLANG: _ClassVar[Language]
    LANGUAGE_FORTRAN: _ClassVar[Language]
    LANGUAGE_FREEFORM: _ClassVar[Language]
    LANGUAGE_GRADLE: _ClassVar[Language]
    LANGUAGE_HACK: _ClassVar[Language]
    LANGUAGE_MAVEN: _ClassVar[Language]
    LANGUAGE_M68KASSEMBLY: _ClassVar[Language]
    LANGUAGE_SAS: _ClassVar[Language]
    LANGUAGE_UNIXASSEMBLY: _ClassVar[Language]
    LANGUAGE_VBA: _ClassVar[Language]
    LANGUAGE_VIMSCRIPT: _ClassVar[Language]
    LANGUAGE_WEBASSEMBLY: _ClassVar[Language]
    LANGUAGE_BLADE: _ClassVar[Language]
    LANGUAGE_ASTRO: _ClassVar[Language]
    LANGUAGE_MUMPS: _ClassVar[Language]
    LANGUAGE_GDSCRIPT: _ClassVar[Language]
    LANGUAGE_NIM: _ClassVar[Language]
    LANGUAGE_PROLOG: _ClassVar[Language]
    LANGUAGE_MARKDOWN_INLINE: _ClassVar[Language]

class ChatMessageSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHAT_MESSAGE_SOURCE_UNSPECIFIED: _ClassVar[ChatMessageSource]
    CHAT_MESSAGE_SOURCE_USER: _ClassVar[ChatMessageSource]
    CHAT_MESSAGE_SOURCE_SYSTEM: _ClassVar[ChatMessageSource]
    CHAT_MESSAGE_SOURCE_UNKNOWN: _ClassVar[ChatMessageSource]

class CodeContextType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CODE_CONTEXT_TYPE_UNSPECIFIED: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_FUNCTION: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_CLASS: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_IMPORT: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_NAIVE_LINECHUNK: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_REFERENCE_FUNCTION: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_REFERENCE_CLASS: _ClassVar[CodeContextType]
    CODE_CONTEXT_TYPE_FILE: _ClassVar[CodeContextType]

class ContextSnippetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTEXT_SNIPPET_TYPE_UNSPECIFIED: _ClassVar[ContextSnippetType]
    CONTEXT_SNIPPET_TYPE_RAW_SOURCE: _ClassVar[ContextSnippetType]
    CONTEXT_SNIPPET_TYPE_SIGNATURE: _ClassVar[ContextSnippetType]
    CONTEXT_SNIPPET_TYPE_NODEPATH: _ClassVar[ContextSnippetType]

class ContextInclusionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTEXT_INCLUSION_TYPE_UNSPECIFIED: _ClassVar[ContextInclusionType]
    CONTEXT_INCLUSION_TYPE_INCLUDE: _ClassVar[ContextInclusionType]
    CONTEXT_INCLUSION_TYPE_EXCLUDE: _ClassVar[ContextInclusionType]

class ExperimentKey(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[ExperimentKey]

class UserTeamStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_TEAM_STATUS_UNSPECIFIED: _ClassVar[UserTeamStatus]
    USER_TEAM_STATUS_PENDING: _ClassVar[UserTeamStatus]
    USER_TEAM_STATUS_APPROVED: _ClassVar[UserTeamStatus]
    USER_TEAM_STATUS_REJECTED: _ClassVar[UserTeamStatus]

class EmbedType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EMBED_TYPE_UNSPECIFIED: _ClassVar[EmbedType]
    EMBED_TYPE_RAW_SOURCE: _ClassVar[EmbedType]
    EMBED_TYPE_DOCSTRING: _ClassVar[EmbedType]
    EMBED_TYPE_FUNCTION: _ClassVar[EmbedType]
    EMBED_TYPE_NODEPATH: _ClassVar[EmbedType]
    EMBED_TYPE_DECLARATION: _ClassVar[EmbedType]
    EMBED_TYPE_NAIVE_CHUNK: _ClassVar[EmbedType]
    EMBED_TYPE_SIGNATURE: _ClassVar[EmbedType]

class ScmProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCM_PROVIDER_UNSPECIFIED: _ClassVar[ScmProvider]
    SCM_PROVIDER_GITHUB: _ClassVar[ScmProvider]
    SCM_PROVIDER_GITLAB: _ClassVar[ScmProvider]
    SCM_PROVIDER_BITBUCKET: _ClassVar[ScmProvider]

class Model(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODEL_UNSPECIFIED: _ClassVar[Model]
    MODEL_CHAT_3_5_TURBO: _ClassVar[Model]
    MODEL_CHAT_GPT_3_5_TURBO_1106: _ClassVar[Model]
    MODEL_CHAT_GPT_4: _ClassVar[Model]
    MODEL_CHAT_GPT_4_1106_PREVIEW: _ClassVar[Model]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_ENABLE_CODEIUM: EventType
EVENT_TYPE_DISABLE_CODEIUM: EventType
EVENT_TYPE_SHOW_PREVIOUS_COMPLETION: EventType
EVENT_TYPE_SHOW_NEXT_COMPLETION: EventType
COMPLETION_SOURCE_UNSPECIFIED: CompletionSource
COMPLETION_SOURCE_TYPING_AS_SUGGESTED: CompletionSource
COMPLETION_SOURCE_CACHE: CompletionSource
COMPLETION_SOURCE_NETWORK: CompletionSource
LANGUAGE_UNSPECIFIED: Language
LANGUAGE_C: Language
LANGUAGE_CLOJURE: Language
LANGUAGE_COFFEESCRIPT: Language
LANGUAGE_CPP: Language
LANGUAGE_CSHARP: Language
LANGUAGE_CSS: Language
LANGUAGE_CUDACPP: Language
LANGUAGE_DOCKERFILE: Language
LANGUAGE_GO: Language
LANGUAGE_GROOVY: Language
LANGUAGE_HANDLEBARS: Language
LANGUAGE_HASKELL: Language
LANGUAGE_HCL: Language
LANGUAGE_HTML: Language
LANGUAGE_INI: Language
LANGUAGE_JAVA: Language
LANGUAGE_JAVASCRIPT: Language
LANGUAGE_JSON: Language
LANGUAGE_JULIA: Language
LANGUAGE_KOTLIN: Language
LANGUAGE_LATEX: Language
LANGUAGE_LESS: Language
LANGUAGE_LUA: Language
LANGUAGE_MAKEFILE: Language
LANGUAGE_MARKDOWN: Language
LANGUAGE_OBJECTIVEC: Language
LANGUAGE_OBJECTIVECPP: Language
LANGUAGE_PERL: Language
LANGUAGE_PHP: Language
LANGUAGE_PLAINTEXT: Language
LANGUAGE_PROTOBUF: Language
LANGUAGE_PBTXT: Language
LANGUAGE_PYTHON: Language
LANGUAGE_R: Language
LANGUAGE_RUBY: Language
LANGUAGE_RUST: Language
LANGUAGE_SASS: Language
LANGUAGE_SCALA: Language
LANGUAGE_SCSS: Language
LANGUAGE_SHELL: Language
LANGUAGE_SQL: Language
LANGUAGE_STARLARK: Language
LANGUAGE_SWIFT: Language
LANGUAGE_TSX: Language
LANGUAGE_TYPESCRIPT: Language
LANGUAGE_VISUALBASIC: Language
LANGUAGE_VUE: Language
LANGUAGE_XML: Language
LANGUAGE_XSL: Language
LANGUAGE_YAML: Language
LANGUAGE_SVELTE: Language
LANGUAGE_TOML: Language
LANGUAGE_DART: Language
LANGUAGE_RST: Language
LANGUAGE_OCAML: Language
LANGUAGE_CMAKE: Language
LANGUAGE_PASCAL: Language
LANGUAGE_ELIXIR: Language
LANGUAGE_FSHARP: Language
LANGUAGE_LISP: Language
LANGUAGE_MATLAB: Language
LANGUAGE_POWERSHELL: Language
LANGUAGE_SOLIDITY: Language
LANGUAGE_ADA: Language
LANGUAGE_OCAML_INTERFACE: Language
LANGUAGE_TREE_SITTER_QUERY: Language
LANGUAGE_APL: Language
LANGUAGE_ASSEMBLY: Language
LANGUAGE_COBOL: Language
LANGUAGE_CRYSTAL: Language
LANGUAGE_EMACS_LISP: Language
LANGUAGE_ERLANG: Language
LANGUAGE_FORTRAN: Language
LANGUAGE_FREEFORM: Language
LANGUAGE_GRADLE: Language
LANGUAGE_HACK: Language
LANGUAGE_MAVEN: Language
LANGUAGE_M68KASSEMBLY: Language
LANGUAGE_SAS: Language
LANGUAGE_UNIXASSEMBLY: Language
LANGUAGE_VBA: Language
LANGUAGE_VIMSCRIPT: Language
LANGUAGE_WEBASSEMBLY: Language
LANGUAGE_BLADE: Language
LANGUAGE_ASTRO: Language
LANGUAGE_MUMPS: Language
LANGUAGE_GDSCRIPT: Language
LANGUAGE_NIM: Language
LANGUAGE_PROLOG: Language
LANGUAGE_MARKDOWN_INLINE: Language
CHAT_MESSAGE_SOURCE_UNSPECIFIED: ChatMessageSource
CHAT_MESSAGE_SOURCE_USER: ChatMessageSource
CHAT_MESSAGE_SOURCE_SYSTEM: ChatMessageSource
CHAT_MESSAGE_SOURCE_UNKNOWN: ChatMessageSource
CODE_CONTEXT_TYPE_UNSPECIFIED: CodeContextType
CODE_CONTEXT_TYPE_FUNCTION: CodeContextType
CODE_CONTEXT_TYPE_CLASS: CodeContextType
CODE_CONTEXT_TYPE_IMPORT: CodeContextType
CODE_CONTEXT_TYPE_NAIVE_LINECHUNK: CodeContextType
CODE_CONTEXT_TYPE_REFERENCE_FUNCTION: CodeContextType
CODE_CONTEXT_TYPE_REFERENCE_CLASS: CodeContextType
CODE_CONTEXT_TYPE_FILE: CodeContextType
CONTEXT_SNIPPET_TYPE_UNSPECIFIED: ContextSnippetType
CONTEXT_SNIPPET_TYPE_RAW_SOURCE: ContextSnippetType
CONTEXT_SNIPPET_TYPE_SIGNATURE: ContextSnippetType
CONTEXT_SNIPPET_TYPE_NODEPATH: ContextSnippetType
CONTEXT_INCLUSION_TYPE_UNSPECIFIED: ContextInclusionType
CONTEXT_INCLUSION_TYPE_INCLUDE: ContextInclusionType
CONTEXT_INCLUSION_TYPE_EXCLUDE: ContextInclusionType
UNSPECIFIED: ExperimentKey
USER_TEAM_STATUS_UNSPECIFIED: UserTeamStatus
USER_TEAM_STATUS_PENDING: UserTeamStatus
USER_TEAM_STATUS_APPROVED: UserTeamStatus
USER_TEAM_STATUS_REJECTED: UserTeamStatus
EMBED_TYPE_UNSPECIFIED: EmbedType
EMBED_TYPE_RAW_SOURCE: EmbedType
EMBED_TYPE_DOCSTRING: EmbedType
EMBED_TYPE_FUNCTION: EmbedType
EMBED_TYPE_NODEPATH: EmbedType
EMBED_TYPE_DECLARATION: EmbedType
EMBED_TYPE_NAIVE_CHUNK: EmbedType
EMBED_TYPE_SIGNATURE: EmbedType
SCM_PROVIDER_UNSPECIFIED: ScmProvider
SCM_PROVIDER_GITHUB: ScmProvider
SCM_PROVIDER_GITLAB: ScmProvider
SCM_PROVIDER_BITBUCKET: ScmProvider
MODEL_UNSPECIFIED: Model
MODEL_CHAT_3_5_TURBO: Model
MODEL_CHAT_GPT_3_5_TURBO_1106: Model
MODEL_CHAT_GPT_4: Model
MODEL_CHAT_GPT_4_1106_PREVIEW: Model

class Completion(_message.Message):
    __slots__ = ("completion_id", "text", "prefix", "stop", "score", "tokens", "decoded_tokens", "probabilities", "adjusted_probabilities", "generated_length")
    COMPLETION_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    DECODED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_PROBABILITIES_FIELD_NUMBER: _ClassVar[int]
    GENERATED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    completion_id: str
    text: str
    prefix: str
    stop: str
    score: float
    tokens: _containers.RepeatedScalarFieldContainer[int]
    decoded_tokens: _containers.RepeatedScalarFieldContainer[str]
    probabilities: _containers.RepeatedScalarFieldContainer[float]
    adjusted_probabilities: _containers.RepeatedScalarFieldContainer[float]
    generated_length: int
    def __init__(self, completion_id: _Optional[str] = ..., text: _Optional[str] = ..., prefix: _Optional[str] = ..., stop: _Optional[str] = ..., score: _Optional[float] = ..., tokens: _Optional[_Iterable[int]] = ..., decoded_tokens: _Optional[_Iterable[str]] = ..., probabilities: _Optional[_Iterable[float]] = ..., adjusted_probabilities: _Optional[_Iterable[float]] = ..., generated_length: _Optional[int] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("ide_name", "ide_version", "extension_name", "extension_version", "api_key", "locale", "session_id", "request_id")
    IDE_NAME_FIELD_NUMBER: _ClassVar[int]
    IDE_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_NAME_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_VERSION_FIELD_NUMBER: _ClassVar[int]
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ide_name: str
    ide_version: str
    extension_name: str
    extension_version: str
    api_key: str
    locale: str
    session_id: str
    request_id: int
    def __init__(self, ide_name: _Optional[str] = ..., ide_version: _Optional[str] = ..., extension_name: _Optional[str] = ..., extension_version: _Optional[str] = ..., api_key: _Optional[str] = ..., locale: _Optional[str] = ..., session_id: _Optional[str] = ..., request_id: _Optional[int] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("event_type", "event_json", "timestamp_unix_ms")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_JSON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_UNIX_MS_FIELD_NUMBER: _ClassVar[int]
    event_type: EventType
    event_json: str
    timestamp_unix_ms: int
    def __init__(self, event_type: _Optional[_Union[EventType, str]] = ..., event_json: _Optional[str] = ..., timestamp_unix_ms: _Optional[int] = ...) -> None: ...

class FunctionInfo(_message.Message):
    __slots__ = ("raw_source", "clean_function", "docstring", "node_name", "params", "definition_line", "start_line", "end_line", "start_col", "end_col", "leading_whitespace", "language")
    RAW_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CLEAN_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    DOCSTRING_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_LINE_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    START_COL_FIELD_NUMBER: _ClassVar[int]
    END_COL_FIELD_NUMBER: _ClassVar[int]
    LEADING_WHITESPACE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    raw_source: str
    clean_function: str
    docstring: str
    node_name: str
    params: str
    definition_line: int
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    leading_whitespace: str
    language: Language
    def __init__(self, raw_source: _Optional[str] = ..., clean_function: _Optional[str] = ..., docstring: _Optional[str] = ..., node_name: _Optional[str] = ..., params: _Optional[str] = ..., definition_line: _Optional[int] = ..., start_line: _Optional[int] = ..., end_line: _Optional[int] = ..., start_col: _Optional[int] = ..., end_col: _Optional[int] = ..., leading_whitespace: _Optional[str] = ..., language: _Optional[_Union[Language, str]] = ...) -> None: ...

class CodeContextItem(_message.Message):
    __slots__ = ("absolute_path", "workspace_paths", "node_name", "node_lineage", "start_line", "start_col", "end_line", "end_col", "context_type", "language", "snippet_by_type")
    class SnippetByTypeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SnippetWithWordCount
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SnippetWithWordCount, _Mapping]] = ...) -> None: ...
    ABSOLUTE_PATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_PATHS_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_LINEAGE_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    START_COL_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    END_COL_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    SNIPPET_BY_TYPE_FIELD_NUMBER: _ClassVar[int]
    absolute_path: str
    workspace_paths: _containers.RepeatedCompositeFieldContainer[WorkspacePath]
    node_name: str
    node_lineage: _containers.RepeatedScalarFieldContainer[str]
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    context_type: CodeContextType
    language: Language
    snippet_by_type: _containers.MessageMap[str, SnippetWithWordCount]
    def __init__(self, absolute_path: _Optional[str] = ..., workspace_paths: _Optional[_Iterable[_Union[WorkspacePath, _Mapping]]] = ..., node_name: _Optional[str] = ..., node_lineage: _Optional[_Iterable[str]] = ..., start_line: _Optional[int] = ..., start_col: _Optional[int] = ..., end_line: _Optional[int] = ..., end_col: _Optional[int] = ..., context_type: _Optional[_Union[CodeContextType, str]] = ..., language: _Optional[_Union[Language, str]] = ..., snippet_by_type: _Optional[_Mapping[str, SnippetWithWordCount]] = ...) -> None: ...

class SnippetWithWordCount(_message.Message):
    __slots__ = ("snippet", "word_count_by_splitter")
    class WordCountBySplitterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: WordCount
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[WordCount, _Mapping]] = ...) -> None: ...
    SNIPPET_FIELD_NUMBER: _ClassVar[int]
    WORD_COUNT_BY_SPLITTER_FIELD_NUMBER: _ClassVar[int]
    snippet: str
    word_count_by_splitter: _containers.MessageMap[str, WordCount]
    def __init__(self, snippet: _Optional[str] = ..., word_count_by_splitter: _Optional[_Mapping[str, WordCount]] = ...) -> None: ...

class WordCount(_message.Message):
    __slots__ = ("word_count_map",)
    class WordCountMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    WORD_COUNT_MAP_FIELD_NUMBER: _ClassVar[int]
    word_count_map: _containers.ScalarMap[str, int]
    def __init__(self, word_count_map: _Optional[_Mapping[str, int]] = ...) -> None: ...

class WorkspacePath(_message.Message):
    __slots__ = ("workspace", "relative_path")
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    relative_path: str
    def __init__(self, workspace: _Optional[str] = ..., relative_path: _Optional[str] = ...) -> None: ...

class UserStatus(_message.Message):
    __slots__ = ("pro", "disable_telemetry", "name", "ignore_chat_telemetry_setting", "team_id", "team_status")
    PRO_FIELD_NUMBER: _ClassVar[int]
    DISABLE_TELEMETRY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IGNORE_CHAT_TELEMETRY_SETTING_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_STATUS_FIELD_NUMBER: _ClassVar[int]
    pro: bool
    disable_telemetry: bool
    name: str
    ignore_chat_telemetry_setting: bool
    team_id: str
    team_status: UserTeamStatus
    def __init__(self, pro: bool = ..., disable_telemetry: bool = ..., name: _Optional[str] = ..., ignore_chat_telemetry_setting: bool = ..., team_id: _Optional[str] = ..., team_status: _Optional[_Union[UserTeamStatus, str]] = ...) -> None: ...

class EmbeddingMetadata(_message.Message):
    __slots__ = ("node_name", "start_line", "end_line", "embed_type")
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    EMBED_TYPE_FIELD_NUMBER: _ClassVar[int]
    node_name: str
    start_line: int
    end_line: int
    embed_type: EmbedType
    def __init__(self, node_name: _Optional[str] = ..., start_line: _Optional[int] = ..., end_line: _Optional[int] = ..., embed_type: _Optional[_Union[EmbedType, str]] = ...) -> None: ...

class UserSettings(_message.Message):
    __slots__ = ("open_most_recent_chat_conversation", "last_selected_model")
    OPEN_MOST_RECENT_CHAT_CONVERSATION_FIELD_NUMBER: _ClassVar[int]
    LAST_SELECTED_MODEL_FIELD_NUMBER: _ClassVar[int]
    open_most_recent_chat_conversation: bool
    last_selected_model: Model
    def __init__(self, open_most_recent_chat_conversation: bool = ..., last_selected_model: _Optional[_Union[Model, str]] = ...) -> None: ...

class GitRepoInfo(_message.Message):
    __slots__ = ("name", "owner", "repo_name", "commit", "version_alias", "scm_provider", "base_git_url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    REPO_NAME_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    VERSION_ALIAS_FIELD_NUMBER: _ClassVar[int]
    SCM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    BASE_GIT_URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    repo_name: str
    commit: str
    version_alias: str
    scm_provider: ScmProvider
    base_git_url: str
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., repo_name: _Optional[str] = ..., commit: _Optional[str] = ..., version_alias: _Optional[str] = ..., scm_provider: _Optional[_Union[ScmProvider, str]] = ..., base_git_url: _Optional[str] = ...) -> None: ...

class EditorOptions(_message.Message):
    __slots__ = ("tab_size", "insert_spaces", "disable_autocomplete_in_comments")
    TAB_SIZE_FIELD_NUMBER: _ClassVar[int]
    INSERT_SPACES_FIELD_NUMBER: _ClassVar[int]
    DISABLE_AUTOCOMPLETE_IN_COMMENTS_FIELD_NUMBER: _ClassVar[int]
    tab_size: int
    insert_spaces: bool
    disable_autocomplete_in_comments: bool
    def __init__(self, tab_size: _Optional[int] = ..., insert_spaces: bool = ..., disable_autocomplete_in_comments: bool = ...) -> None: ...
