from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Client(_message.Message):
    __slots__ = ["client_id"]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    def __init__(self, client_id: _Optional[str] = ...) -> None: ...

class DeletePRtoRepl(_message.Message):
    __slots__ = ["Version", "uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    Version: _timestamp_pb2.Timestamp
    uuid: str
    def __init__(self, uuid: _Optional[str] = ..., Version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ["Status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    Status: str
    def __init__(self, Status: _Optional[str] = ...) -> None: ...

class GetReplicaListRequest(_message.Message):
    __slots__ = ["client"]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    client: Client
    def __init__(self, client: _Optional[_Union[Client, _Mapping]] = ...) -> None: ...

class GetReplicaListResponse(_message.Message):
    __slots__ = ["replica_list"]
    REPLICA_LIST_FIELD_NUMBER: _ClassVar[int]
    replica_list: _containers.RepeatedCompositeFieldContainer[Server]
    def __init__(self, replica_list: _Optional[_Iterable[_Union[Server, _Mapping]]] = ...) -> None: ...

class NotifyPrimaryRequest(_message.Message):
    __slots__ = ["replicaAddress"]
    REPLICAADDRESS_FIELD_NUMBER: _ClassVar[int]
    replicaAddress: str
    def __init__(self, replicaAddress: _Optional[str] = ...) -> None: ...

class NotifyPrimaryResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ["Content", "Name", "Status", "Version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    Content: str
    NAME_FIELD_NUMBER: _ClassVar[int]
    Name: str
    STATUS_FIELD_NUMBER: _ClassVar[int]
    Status: str
    VERSION_FIELD_NUMBER: _ClassVar[int]
    Version: _timestamp_pb2.Timestamp
    def __init__(self, Status: _Optional[str] = ..., Name: _Optional[str] = ..., Content: _Optional[str] = ..., Version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RegisterServerRequest(_message.Message):
    __slots__ = ["address"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class RegisterServerResponse(_message.Message):
    __slots__ = ["message", "primaryServerAddress", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PRIMARYSERVERADDRESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    primaryServerAddress: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ..., primaryServerAddress: _Optional[str] = ...) -> None: ...

class Server(_message.Message):
    __slots__ = ["address"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class WritePRtoReplRequest(_message.Message):
    __slots__ = ["Content", "Name", "Version", "uuid"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    Content: str
    NAME_FIELD_NUMBER: _ClassVar[int]
    Name: str
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    Version: _timestamp_pb2.Timestamp
    uuid: str
    def __init__(self, Name: _Optional[str] = ..., Content: _Optional[str] = ..., uuid: _Optional[str] = ..., Version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WritePRtoReplResponse(_message.Message):
    __slots__ = ["Status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    Status: str
    def __init__(self, Status: _Optional[str] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ["Content", "Name", "uuid"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    Content: str
    NAME_FIELD_NUMBER: _ClassVar[int]
    Name: str
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, Name: _Optional[str] = ..., Content: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ["Status", "Version", "uuid"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    Status: str
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    Version: _timestamp_pb2.Timestamp
    uuid: str
    def __init__(self, Status: _Optional[str] = ..., uuid: _Optional[str] = ..., Version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
