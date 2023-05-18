from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MapTaskAssignmentRequest(_message.Message):
    __slots__ = ["DocIDs", "R", "assigned_input_splits"]
    ASSIGNED_INPUT_SPLITS_FIELD_NUMBER: _ClassVar[int]
    DOCIDS_FIELD_NUMBER: _ClassVar[int]
    DocIDs: _containers.RepeatedScalarFieldContainer[int]
    R: int
    R_FIELD_NUMBER: _ClassVar[int]
    assigned_input_splits: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, assigned_input_splits: _Optional[_Iterable[str]] = ..., DocIDs: _Optional[_Iterable[int]] = ..., R: _Optional[int] = ...) -> None: ...

class MapperDoneRequest(_message.Message):
    __slots__ = ["address", "interim_files", "partitions"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INTERIM_FILES_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    address: str
    interim_files: _containers.RepeatedScalarFieldContainer[str]
    partitions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, interim_files: _Optional[_Iterable[str]] = ..., address: _Optional[str] = ..., partitions: _Optional[_Iterable[int]] = ...) -> None: ...

class ReduceTaskAssignmentRequest(_message.Message):
    __slots__ = ["assigned_interim_files", "output_data_loc"]
    ASSIGNED_INTERIM_FILES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_DATA_LOC_FIELD_NUMBER: _ClassVar[int]
    assigned_interim_files: _containers.RepeatedScalarFieldContainer[str]
    output_data_loc: str
    def __init__(self, assigned_interim_files: _Optional[_Iterable[str]] = ..., output_data_loc: _Optional[str] = ...) -> None: ...

class ReducerDoneRequest(_message.Message):
    __slots__ = ["address", "interim_files"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INTERIM_FILES_FIELD_NUMBER: _ClassVar[int]
    address: str
    interim_files: str
    def __init__(self, interim_files: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ["address", "name"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
