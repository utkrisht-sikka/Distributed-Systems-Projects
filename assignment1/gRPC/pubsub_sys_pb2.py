# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pubsub_sys.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10pubsub_sys.proto\x12\rpubsub_system\x1a\x1fgoogle/protobuf/timestamp.proto\"\'\n\x06Server\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\")\n\x06\x43lient\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tunique_id\x18\x02 \x01(\t\"~\n\x07\x41rticle\x12(\n\x04type\x18\x01 \x01(\x0e\x32\x1a.pubsub_system.ArticleType\x12\x0e\n\x06\x61uthor\x18\x02 \x01(\t\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\"6\n\x15RegisterServerRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"9\n\x16RegisterServerResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"=\n\x14GetServerListRequest\x12%\n\x06\x63lient\x18\x01 \x01(\x0b\x32\x15.pubsub_system.Client\"C\n\x15GetServerListResponse\x12*\n\x0bserver_list\x18\x01 \x03(\x0b\x32\x15.pubsub_system.Server\"&\n\x11ServerJoinRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\"5\n\x12ServerJoinResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"\'\n\x12ServerLeaveRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\"6\n\x13ServerLeaveResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"\xd9\x01\n\x15PublishArticleRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12J\n\x07\x61rticle\x18\x02 \x01(\x0b\x32\x39.pubsub_system.PublishArticleRequest.ArticlePublishFormat\x1a\x61\n\x14\x41rticlePublishFormat\x12(\n\x04type\x18\x01 \x01(\x0e\x32\x1a.pubsub_system.ArticleType\x12\x0e\n\x06\x61uthor\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"9\n\x16PublishArticleResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"\xf4\x01\n\x12GetArticlesRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12O\n\x0f\x61rticle_request\x18\x02 \x01(\x0b\x32\x36.pubsub_system.GetArticlesRequest.ArticleRequestFormat\x1az\n\x14\x41rticleRequestFormat\x12(\n\x04type\x18\x01 \x01(\x0e\x32\x1a.pubsub_system.ArticleType\x12\x0e\n\x06\x61uthor\x18\x02 \x01(\t\x12(\n\x04time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"`\n\x13GetArticlesResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12(\n\x08\x61rticles\x18\x03 \x03(\x0b\x32\x16.pubsub_system.Article*I\n\x0b\x41rticleType\x12\x08\n\x04NONE\x10\x00\x12\n\n\x06SPORTS\x10\x01\x12\x0b\n\x07\x46\x41SHION\x10\x02\x12\x0c\n\x08POLITICS\x10\x03\x12\t\n\x05\x42LANK\x10\x04\x32\xd0\x01\n\x0fRegistryService\x12_\n\x0eRegisterServer\x12$.pubsub_system.RegisterServerRequest\x1a%.pubsub_system.RegisterServerResponse\"\x00\x12\\\n\rGetServerList\x12#.pubsub_system.GetServerListRequest\x1a$.pubsub_system.GetServerListResponse\"\x00\x32\xf5\x02\n\rServerService\x12S\n\nJoinServer\x12 .pubsub_system.ServerJoinRequest\x1a!.pubsub_system.ServerJoinResponse\"\x00\x12V\n\x0bLeaveServer\x12!.pubsub_system.ServerLeaveRequest\x1a\".pubsub_system.ServerLeaveResponse\"\x00\x12V\n\x0bGetArticles\x12!.pubsub_system.GetArticlesRequest\x1a\".pubsub_system.GetArticlesResponse\"\x00\x12_\n\x0ePublishArticle\x12$.pubsub_system.PublishArticleRequest\x1a%.pubsub_system.PublishArticleResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pubsub_sys_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ARTICLETYPE._serialized_start=1343
  _ARTICLETYPE._serialized_end=1416
  _SERVER._serialized_start=68
  _SERVER._serialized_end=107
  _CLIENT._serialized_start=109
  _CLIENT._serialized_end=150
  _ARTICLE._serialized_start=152
  _ARTICLE._serialized_end=278
  _REGISTERSERVERREQUEST._serialized_start=280
  _REGISTERSERVERREQUEST._serialized_end=334
  _REGISTERSERVERRESPONSE._serialized_start=336
  _REGISTERSERVERRESPONSE._serialized_end=393
  _GETSERVERLISTREQUEST._serialized_start=395
  _GETSERVERLISTREQUEST._serialized_end=456
  _GETSERVERLISTRESPONSE._serialized_start=458
  _GETSERVERLISTRESPONSE._serialized_end=525
  _SERVERJOINREQUEST._serialized_start=527
  _SERVERJOINREQUEST._serialized_end=565
  _SERVERJOINRESPONSE._serialized_start=567
  _SERVERJOINRESPONSE._serialized_end=620
  _SERVERLEAVEREQUEST._serialized_start=622
  _SERVERLEAVEREQUEST._serialized_end=661
  _SERVERLEAVERESPONSE._serialized_start=663
  _SERVERLEAVERESPONSE._serialized_end=717
  _PUBLISHARTICLEREQUEST._serialized_start=720
  _PUBLISHARTICLEREQUEST._serialized_end=937
  _PUBLISHARTICLEREQUEST_ARTICLEPUBLISHFORMAT._serialized_start=840
  _PUBLISHARTICLEREQUEST_ARTICLEPUBLISHFORMAT._serialized_end=937
  _PUBLISHARTICLERESPONSE._serialized_start=939
  _PUBLISHARTICLERESPONSE._serialized_end=996
  _GETARTICLESREQUEST._serialized_start=999
  _GETARTICLESREQUEST._serialized_end=1243
  _GETARTICLESREQUEST_ARTICLEREQUESTFORMAT._serialized_start=1121
  _GETARTICLESREQUEST_ARTICLEREQUESTFORMAT._serialized_end=1243
  _GETARTICLESRESPONSE._serialized_start=1245
  _GETARTICLESRESPONSE._serialized_end=1341
  _REGISTRYSERVICE._serialized_start=1419
  _REGISTRYSERVICE._serialized_end=1627
  _SERVERSERVICE._serialized_start=1630
  _SERVERSERVICE._serialized_end=2003
# @@protoc_insertion_point(module_scope)