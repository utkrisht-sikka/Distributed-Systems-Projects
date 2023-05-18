from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Client(_message.Message):
    __slots__ = ["client_id", "name"]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    name: str
    def __init__(self, name: _Optional[str] = ..., client_id: _Optional[str] = ...) -> None: ...

class ClientDeleteReplicaRequest(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ClientDeleteReplicaResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ClientReadReplicaRequest(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ClientReadReplicaResponse(_message.Message):
    __slots__ = ["content", "name", "status", "version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    status: str
    version: _timestamp_pb2.Timestamp
    def __init__(self, status: _Optional[str] = ..., name: _Optional[str] = ..., content: _Optional[str] = ..., version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ClientWriteReplicaRequest(_message.Message):
    __slots__ = ["content", "name", "uuid"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    uuid: str
    def __init__(self, name: _Optional[str] = ..., content: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class ClientWriteReplicaResponse(_message.Message):
    __slots__ = ["status", "uuid", "version"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    uuid: str
    version: _timestamp_pb2.Timestamp
    def __init__(self, status: _Optional[str] = ..., uuid: _Optional[str] = ..., version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ForwardDeletePrimaryRequest(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ForwardDeletePrimaryResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ForwardWritePrimaryRequest(_message.Message):
    __slots__ = ["content", "name", "uuid"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    uuid: str
    def __init__(self, name: _Optional[str] = ..., uuid: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ForwardWritePrimaryResponse(_message.Message):
    __slots__ = ["message", "status", "uuid", "version"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    uuid: str
    version: _timestamp_pb2.Timestamp
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ..., uuid: _Optional[str] = ..., version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetReplicaListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

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

class PrimaryDeleteReplicaRequest(_message.Message):
    __slots__ = ["uuid", "version"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    version: _timestamp_pb2.Timestamp
    def __init__(self, uuid: _Optional[str] = ..., version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PrimaryDeleteReplicaResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class PrimaryWriteReplicaRequest(_message.Message):
    __slots__ = ["content", "name", "uuid", "version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    uuid: str
    version: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., uuid: _Optional[str] = ..., content: _Optional[str] = ..., version: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PrimaryWriteReplicaResponse(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    def __init__(self, status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

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
