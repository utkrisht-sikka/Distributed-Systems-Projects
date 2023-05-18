from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddMapperRequest(_message.Message):
    __slots__ = ["ip", "port"]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: str
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class AddReducerRequest(_message.Message):
    __slots__ = ["ip", "port"]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: str
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class GeneralMessageResponse(_message.Message):
    __slots__ = ["message_val"]
    MESSAGE_VAL_FIELD_NUMBER: _ClassVar[int]
    message_val: str
    def __init__(self, message_val: _Optional[str] = ...) -> None: ...

class GeneralRequest(_message.Message):
    __slots__ = ["message_val"]
    MESSAGE_VAL_FIELD_NUMBER: _ClassVar[int]
    message_val: str
    def __init__(self, message_val: _Optional[str] = ...) -> None: ...

class GeneralResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...
