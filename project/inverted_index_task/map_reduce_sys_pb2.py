# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: map_reduce_sys.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14map_reduce_sys.proto\x12\x0emap_reduce_sys\"<\n\x12ReducerDoneRequest\x12\x15\n\rinterim_files\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"O\n\x11MapperDoneRequest\x12\x15\n\rinterim_files\x18\x01 \x03(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\x12\x12\n\npartitions\x18\x04 \x03(\x05\"0\n\x0fRegisterRequest\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"+\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"T\n\x18MapTaskAssignmentRequest\x12\x1d\n\x15\x61ssigned_input_splits\x18\x01 \x03(\t\x12\x0e\n\x06\x44ocIDs\x18\x02 \x03(\x05\x12\t\n\x01R\x18\x03 \x01(\x05\"V\n\x1bReduceTaskAssignmentRequest\x12\x1e\n\x16\x61ssigned_interim_files\x18\x01 \x03(\t\x12\x17\n\x0foutput_data_loc\x18\x02 \x01(\t2\xf4\x01\n\rMasterService\x12G\n\x08Register\x12\x1f.map_reduce_sys.RegisterRequest\x1a\x18.map_reduce_sys.Response\"\x00\x12K\n\nMapperDone\x12!.map_reduce_sys.MapperDoneRequest\x1a\x18.map_reduce_sys.Response\"\x00\x12M\n\x0bReducerDone\x12\".map_reduce_sys.ReducerDoneRequest\x1a\x18.map_reduce_sys.Response\"\x00\x32j\n\rMapperService\x12Y\n\x11MapTaskAssignment\x12(.map_reduce_sys.MapTaskAssignmentRequest\x1a\x18.map_reduce_sys.Response\"\x00\x32q\n\x0eReducerService\x12_\n\x14ReduceTaskAssignment\x12+.map_reduce_sys.ReduceTaskAssignmentRequest\x1a\x18.map_reduce_sys.Response\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'map_reduce_sys_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REDUCERDONEREQUEST._serialized_start=40
  _REDUCERDONEREQUEST._serialized_end=100
  _MAPPERDONEREQUEST._serialized_start=102
  _MAPPERDONEREQUEST._serialized_end=181
  _REGISTERREQUEST._serialized_start=183
  _REGISTERREQUEST._serialized_end=231
  _RESPONSE._serialized_start=233
  _RESPONSE._serialized_end=276
  _MAPTASKASSIGNMENTREQUEST._serialized_start=278
  _MAPTASKASSIGNMENTREQUEST._serialized_end=362
  _REDUCETASKASSIGNMENTREQUEST._serialized_start=364
  _REDUCETASKASSIGNMENTREQUEST._serialized_end=450
  _MASTERSERVICE._serialized_start=453
  _MASTERSERVICE._serialized_end=697
  _MAPPERSERVICE._serialized_start=699
  _MAPPERSERVICE._serialized_end=805
  _REDUCERSERVICE._serialized_start=807
  _REDUCERSERVICE._serialized_end=920
# @@protoc_insertion_point(module_scope)
