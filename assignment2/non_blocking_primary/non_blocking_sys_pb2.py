# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: non_blocking_sys.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16non_blocking_sys.proto\x12\x1fnon_blocking_primary_backup_sys\x1a\x1fgoogle/protobuf/timestamp.proto\"\x19\n\x06Server\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\")\n\x06\x43lient\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tclient_id\x18\x02 \x01(\t\"(\n\x15RegisterServerRequest\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"W\n\x16RegisterServerResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x1c\n\x14primaryServerAddress\x18\x03 \x01(\t\"\x17\n\x15GetReplicaListRequest\"W\n\x16GetReplicaListResponse\x12=\n\x0creplica_list\x18\x01 \x03(\x0b\x32\'.non_blocking_primary_backup_sys.Server\".\n\x14NotifyPrimaryRequest\x12\x16\n\x0ereplicaAddress\x18\x01 \x01(\t\"8\n\x15NotifyPrimaryResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"H\n\x19\x43lientWriteReplicaRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x0c\n\x04uuid\x18\x03 \x01(\t\"g\n\x1a\x43lientWriteReplicaResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0c\n\x04uuid\x18\x02 \x01(\t\x12+\n\x07version\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"v\n\x1aPrimaryWriteReplicaRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04uuid\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12+\n\x07version\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\">\n\x1bPrimaryWriteReplicaResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"I\n\x1a\x46orwardWritePrimaryRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04uuid\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"y\n\x1b\x46orwardWritePrimaryResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0c\n\x04uuid\x18\x03 \x01(\t\x12+\n\x07version\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"(\n\x18\x43lientReadReplicaRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\"w\n\x19\x43lientReadReplicaResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12+\n\x07version\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"*\n\x1a\x43lientDeleteReplicaRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\"-\n\x1b\x43lientDeleteReplicaResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"+\n\x1b\x46orwardDeletePrimaryRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\"?\n\x1c\x46orwardDeletePrimaryResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"X\n\x1bPrimaryDeleteReplicaRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12+\n\x07version\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"?\n\x1cPrimaryDeleteReplicaResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t2\x9d\x02\n\x0fRegistryService\x12\x83\x01\n\x0eRegisterServer\x12\x36.non_blocking_primary_backup_sys.RegisterServerRequest\x1a\x37.non_blocking_primary_backup_sys.RegisterServerResponse\"\x00\x12\x83\x01\n\x0eGetReplicaList\x12\x36.non_blocking_primary_backup_sys.GetReplicaListRequest\x1a\x37.non_blocking_primary_backup_sys.GetReplicaListResponse\"\x00\x32\xa2\t\n\rServerService\x12\x80\x01\n\rNotifyPrimary\x12\x35.non_blocking_primary_backup_sys.NotifyPrimaryRequest\x1a\x36.non_blocking_primary_backup_sys.NotifyPrimaryResponse\"\x00\x12\x8f\x01\n\x12\x43lientWriteReplica\x12:.non_blocking_primary_backup_sys.ClientWriteReplicaRequest\x1a;.non_blocking_primary_backup_sys.ClientWriteReplicaResponse\"\x00\x12\x92\x01\n\x13\x46orwardWritePrimary\x12;.non_blocking_primary_backup_sys.ForwardWritePrimaryRequest\x1a<.non_blocking_primary_backup_sys.ForwardWritePrimaryResponse\"\x00\x12\x92\x01\n\x13PrimaryWriteReplica\x12;.non_blocking_primary_backup_sys.PrimaryWriteReplicaRequest\x1a<.non_blocking_primary_backup_sys.PrimaryWriteReplicaResponse\"\x00\x12\x8c\x01\n\x11\x43lientReadReplica\x12\x39.non_blocking_primary_backup_sys.ClientReadReplicaRequest\x1a:.non_blocking_primary_backup_sys.ClientReadReplicaResponse\"\x00\x12\x92\x01\n\x13\x43lientDeleteReplica\x12;.non_blocking_primary_backup_sys.ClientDeleteReplicaRequest\x1a<.non_blocking_primary_backup_sys.ClientDeleteReplicaResponse\"\x00\x12\x95\x01\n\x14\x46orwardDeletePrimary\x12<.non_blocking_primary_backup_sys.ForwardDeletePrimaryRequest\x1a=.non_blocking_primary_backup_sys.ForwardDeletePrimaryResponse\"\x00\x12\x95\x01\n\x14PrimaryDeleteReplica\x12<.non_blocking_primary_backup_sys.PrimaryDeleteReplicaRequest\x1a=.non_blocking_primary_backup_sys.PrimaryDeleteReplicaResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'non_blocking_sys_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SERVER._serialized_start=92
  _SERVER._serialized_end=117
  _CLIENT._serialized_start=119
  _CLIENT._serialized_end=160
  _REGISTERSERVERREQUEST._serialized_start=162
  _REGISTERSERVERREQUEST._serialized_end=202
  _REGISTERSERVERRESPONSE._serialized_start=204
  _REGISTERSERVERRESPONSE._serialized_end=291
  _GETREPLICALISTREQUEST._serialized_start=293
  _GETREPLICALISTREQUEST._serialized_end=316
  _GETREPLICALISTRESPONSE._serialized_start=318
  _GETREPLICALISTRESPONSE._serialized_end=405
  _NOTIFYPRIMARYREQUEST._serialized_start=407
  _NOTIFYPRIMARYREQUEST._serialized_end=453
  _NOTIFYPRIMARYRESPONSE._serialized_start=455
  _NOTIFYPRIMARYRESPONSE._serialized_end=511
  _CLIENTWRITEREPLICAREQUEST._serialized_start=513
  _CLIENTWRITEREPLICAREQUEST._serialized_end=585
  _CLIENTWRITEREPLICARESPONSE._serialized_start=587
  _CLIENTWRITEREPLICARESPONSE._serialized_end=690
  _PRIMARYWRITEREPLICAREQUEST._serialized_start=692
  _PRIMARYWRITEREPLICAREQUEST._serialized_end=810
  _PRIMARYWRITEREPLICARESPONSE._serialized_start=812
  _PRIMARYWRITEREPLICARESPONSE._serialized_end=874
  _FORWARDWRITEPRIMARYREQUEST._serialized_start=876
  _FORWARDWRITEPRIMARYREQUEST._serialized_end=949
  _FORWARDWRITEPRIMARYRESPONSE._serialized_start=951
  _FORWARDWRITEPRIMARYRESPONSE._serialized_end=1072
  _CLIENTREADREPLICAREQUEST._serialized_start=1074
  _CLIENTREADREPLICAREQUEST._serialized_end=1114
  _CLIENTREADREPLICARESPONSE._serialized_start=1116
  _CLIENTREADREPLICARESPONSE._serialized_end=1235
  _CLIENTDELETEREPLICAREQUEST._serialized_start=1237
  _CLIENTDELETEREPLICAREQUEST._serialized_end=1279
  _CLIENTDELETEREPLICARESPONSE._serialized_start=1281
  _CLIENTDELETEREPLICARESPONSE._serialized_end=1326
  _FORWARDDELETEPRIMARYREQUEST._serialized_start=1328
  _FORWARDDELETEPRIMARYREQUEST._serialized_end=1371
  _FORWARDDELETEPRIMARYRESPONSE._serialized_start=1373
  _FORWARDDELETEPRIMARYRESPONSE._serialized_end=1436
  _PRIMARYDELETEREPLICAREQUEST._serialized_start=1438
  _PRIMARYDELETEREPLICAREQUEST._serialized_end=1526
  _PRIMARYDELETEREPLICARESPONSE._serialized_start=1528
  _PRIMARYDELETEREPLICARESPONSE._serialized_end=1591
  _REGISTRYSERVICE._serialized_start=1594
  _REGISTRYSERVICE._serialized_end=1879
  _SERVERSERVICE._serialized_start=1882
  _SERVERSERVICE._serialized_end=3068
# @@protoc_insertion_point(module_scope)