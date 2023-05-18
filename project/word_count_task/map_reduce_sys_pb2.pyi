from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MapTaskAssignmentRequest(_message.Message):
    __slots__ = ["R", "assigned_input_splits"]
    ASSIGNED_INPUT_SPLITS_FIELD_NUMBER: _ClassVar[int]
    R: int
    R_FIELD_NUMBER: _ClassVar[int]
    assigned_input_splits: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, assigned_input_splits: _Optional[_Iterable[str]] = ..., R: _Optional[int] = ...) -> None: ...

class MapTaskAssignmentResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class MapWorkerNotificationRequest(_message.Message):
    __slots__ = ["partition_files", "task_status", "worker_address"]
    PARTITION_FILES_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    WORKER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    partition_files: _containers.RepeatedScalarFieldContainer[str]
    task_status: str
    worker_address: str
    def __init__(self, worker_address: _Optional[str] = ..., task_status: _Optional[str] = ..., partition_files: _Optional[_Iterable[str]] = ...) -> None: ...

class MapWorkerNotificationResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ReduceTaskAssignmentRequest(_message.Message):
    __slots__ = ["assigned_partitions", "output_data_loc", "reducer_num"]
    ASSIGNED_PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_DATA_LOC_FIELD_NUMBER: _ClassVar[int]
    REDUCER_NUM_FIELD_NUMBER: _ClassVar[int]
    assigned_partitions: _containers.RepeatedScalarFieldContainer[str]
    output_data_loc: str
    reducer_num: int
    def __init__(self, assigned_partitions: _Optional[_Iterable[str]] = ..., reducer_num: _Optional[int] = ..., output_data_loc: _Optional[str] = ...) -> None: ...

class ReduceTaskAssignmentResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ReduceWorkerNotificationRequest(_message.Message):
    __slots__ = ["reducer_local_output_loc", "task_status", "worker_address"]
    REDUCER_LOCAL_OUTPUT_LOC_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    WORKER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    reducer_local_output_loc: str
    task_status: str
    worker_address: str
    def __init__(self, worker_address: _Optional[str] = ..., task_status: _Optional[str] = ..., reducer_local_output_loc: _Optional[str] = ...) -> None: ...

class ReduceWorkerNotificationResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class RegisterWorkerRequest(_message.Message):
    __slots__ = ["address", "worker_type"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    WORKER_TYPE_FIELD_NUMBER: _ClassVar[int]
    address: str
    worker_type: str
    def __init__(self, address: _Optional[str] = ..., worker_type: _Optional[str] = ...) -> None: ...

class RegisterWorkerResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
