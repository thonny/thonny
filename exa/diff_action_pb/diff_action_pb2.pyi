from exa.codeium_common_pb import codeium_common_pb2 as _codeium_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnifiedDiffLineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNIFIED_DIFF_LINE_TYPE_UNSPECIFIED: _ClassVar[UnifiedDiffLineType]
    UNIFIED_DIFF_LINE_TYPE_INSERT: _ClassVar[UnifiedDiffLineType]
    UNIFIED_DIFF_LINE_TYPE_DELETE: _ClassVar[UnifiedDiffLineType]
    UNIFIED_DIFF_LINE_TYPE_UNCHANGED: _ClassVar[UnifiedDiffLineType]
UNIFIED_DIFF_LINE_TYPE_UNSPECIFIED: UnifiedDiffLineType
UNIFIED_DIFF_LINE_TYPE_INSERT: UnifiedDiffLineType
UNIFIED_DIFF_LINE_TYPE_DELETE: UnifiedDiffLineType
UNIFIED_DIFF_LINE_TYPE_UNCHANGED: UnifiedDiffLineType

class UnifiedDiff(_message.Message):
    __slots__ = ("lines",)
    class UnifiedDiffLine(_message.Message):
        __slots__ = ("text", "type")
        TEXT_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        text: str
        type: UnifiedDiffLineType
        def __init__(self, text: _Optional[str] = ..., type: _Optional[_Union[UnifiedDiffLineType, str]] = ...) -> None: ...
    LINES_FIELD_NUMBER: _ClassVar[int]
    lines: _containers.RepeatedCompositeFieldContainer[UnifiedDiff.UnifiedDiffLine]
    def __init__(self, lines: _Optional[_Iterable[_Union[UnifiedDiff.UnifiedDiffLine, _Mapping]]] = ...) -> None: ...

class DiffBlock(_message.Message):
    __slots__ = ("start_line", "end_line", "unified_diff", "from_language", "to_language")
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    UNIFIED_DIFF_FIELD_NUMBER: _ClassVar[int]
    FROM_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TO_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    start_line: int
    end_line: int
    unified_diff: UnifiedDiff
    from_language: _codeium_common_pb2.Language
    to_language: _codeium_common_pb2.Language
    def __init__(self, start_line: _Optional[int] = ..., end_line: _Optional[int] = ..., unified_diff: _Optional[_Union[UnifiedDiff, _Mapping]] = ..., from_language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ..., to_language: _Optional[_Union[_codeium_common_pb2.Language, str]] = ...) -> None: ...
