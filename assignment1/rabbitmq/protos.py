from enum import Enum

import json
from dataclasses import dataclass
from typing import List
from datetime import datetime
@dataclass
class RPC_Server_Response:
    status: str
    response: dict
    server_name: str
    server_port: str
    @staticmethod
    def from_dict(obj) -> 'RPC_Server_Response':
        _status = str(obj.get("status"))
        _response = json.loads(str(obj.get("response"))) if type(obj.get("response"))!=type("") else str(obj.get("response"));
        _server_name = str(obj.get("server_name"))
        _server_port = str(obj.get("server_port"))

        return RPC_Server_Response(_status, _response,_server_name,_server_port)
@dataclass
class RPC_General:
    req_type: str
    request: dict
    @staticmethod
    def from_dict(obj) -> 'RPC_General':
        _req_type = str(obj.get("req_type"))
        _request = json.loads(obj.get("request"))
        return RPC_General(_req_type, _request)
@dataclass
class Register_Server:
    server_name: str
    server_ip: str
    @staticmethod
    def from_dict(obj) -> 'Register_Server':
        _server_name = str(obj.get("server_name"))
        _server_ip = str(obj.get("server_ip"))
        return Register_Server(_server_name, _server_ip)
@dataclass
class Get_Server_List:
    uuid : str
    ip: str
    port: str
    isServer: bool
    @staticmethod
    def from_dict(obj) -> 'Get_Server_List':
        _uuid = str(obj.get("uuid"))
        _ip = str(obj.get("ip"))
        _port = str(obj.get("port"))
        _isServer = True if(str(obj.get("isServer")).lower()=="true") else False;

        return Get_Server_List(_uuid, _ip, _port,_isServer)
@dataclass
class Join_Server:
    uuid : str
    child_name: str
    child_port: str
    parent_name: str
    parent_port: str
    isServer: bool
    @staticmethod
    def from_dict(obj) -> 'Join_Server':
        _uuid = str(obj.get("uuid"))
        _child_name = str(obj.get("child_name"))
        _child_port = str(obj.get("child_port"))
        _parent_name = str(obj.get("parent_name"))
        _parent_port = str(obj.get("parent_port"))

        _isServer = True if(str(obj.get("isServer")).lower()=="true") else False;

        return Join_Server(_uuid, _child_name, _child_port,_parent_name,_parent_port,_isServer)
@dataclass
class Leave_Server:
    uuid : str
    server_name: str
    server_port: str
    isServer: bool
    @staticmethod
    def from_dict(obj) -> 'Leave_Server':
        _uuid = str(obj.get("uuid"))
        _name = str(obj.get("server_name"))
        _port = str(obj.get("server_port"))
        _isServer = True if(str(obj.get("isServer")).lower()=="true") else False;

        return Leave_Server(_uuid, _name, _port,_isServer)
@dataclass
class RegisterServerRequest:
    request_type: str
    client_uuid: str = ""
    server_name: str = ""
    server_port: str = ""
    @staticmethod
    def from_dict(obj) -> 'RegisterServerRequest':
        _request_type = str(obj.get("request_type"))
        _client_uuid = str(obj.get("client_uuid"))
        _server_name = str(obj.get("server_name"))
        _server_port = str(obj.get("server_port"));
        return RegisterServerRequest(_request_type,_client_uuid,_server_name,_server_port);

@dataclass
class Get_Articles:
    client_uuid: str
    type: str
    author: str
    time: str
    @staticmethod
    def from_dict(obj) -> 'Get_Articles':
        _uuid = str(obj.get("client_uuid"))
        _type = str(obj.get("type"))
        _author = str(obj.get("author"))
        _time = str(obj.get("time"));

        return Get_Articles(_uuid, _type, _author,_time)
@dataclass
class Publish_Article:
    client_uuid: str
    type: str
    author: str
    time: datetime
    content: str
    server_name: str
    server_port: str
    @staticmethod
    def from_dict(obj) -> 'Publish_Article':
        _uuid = str(obj.get("client_uuid"))
        _type = str(obj.get("type"))
        _author = str(obj.get("author"))
        # _time = datetime.strptime(str(obj.get("time")), '%d/%m/%y ');
        _time = str(obj.get("time"));
        _content = str(obj.get("content"));
        _server_name = str(obj.get("server_name"))
        _server_port = str(obj.get("server_port"))
        

        return Publish_Article(_uuid, _type, _author,_time,_content,_server_name,_server_port)
@dataclass
class Article:
    type: str
    author: str
    time: str
    content: str
    uuid: str
    @staticmethod
    def from_dict(obj) -> 'Article':
        _type = str(obj.get("type"))
        _author = str(obj.get("author"))
        _time = str(obj.get("time"));
        _content = str(obj.get("content"));
        _uuid = str(obj.get("uuid"))
        return Article( _type, _author,_time,_content,_uuid)
@dataclass
class List_Articles:
    articles: List[Article]
    server_names: List[str]
    server_ports: List[str]
    @staticmethod
    def from_dict(obj) -> 'List_Articles':
        _articles,_server_names,_server_ports = list(),list(),list()
        _articles.extend([Article.from_dict(y) for y in obj.get("articles",[])])
        _server_names.extend([str(y) for y in obj.get("server_names",[])])
        _server_ports.extend([str(y) for y in obj.get("server_ports",[])])
        return List_Articles(_articles,_server_names,_server_ports);

@dataclass
class Filter_Article:
    time: str 
    type : str
    author: str
    server_name: str
    server_port: str
    @staticmethod
    def from_dict(obj) -> 'Filter_Article':
        _time = str(obj.get("time"));
        _type = str(obj.get("type"));
        _author = str(obj.get("author"));
        _server_name = str(obj.get("server_name"));
        _server_port = str(obj.get("server_port"));
        return Filter_Article(_time,_type,_author,_server_name,_server_port);

class Queues(Enum):
    #for server request and response type
    SERVER_REQUEST_QUEUE = "SERVER_REQUEST_QUEUE";
    SERVER_RESPONSE_QUEUE = "SERVER_RESPONSE_QUEUE";

    CLIENT_REQUEST_QUEUE = "CLIENT_REQUEST_QUEUE";
    CLIENT_RESPONSE_QUEUE = "CLIENT_RESPONSE_QUEUE";

    #for bonus part article sending
    FETCH_REQUEST_QUEUE = "FETCH_REQUEST_QUEUE";
    FETCH_RESPONSE_QUEUE = "FETCH_RESPONSE_QUEUE";

    #for registry server request and response
    REGISTRY_SERVER_REQUEST_QUEUE = "REGISTRY_SERVER_REQUEST_QUEUE";
    REGISTRY_SERVER_RESPONSE_QUEUE = "REGISTRY_SERVER_RESPONSE_QUEUE";
class Exchanges(Enum):
    COMMON_EXCHANGE = "COMMON_EXCHANGE";

class ARTICLE_TYPE(Enum):
    SPORTS = "SPORTS";
    FASHION = "FASHION";
    POLITICS = "POLITICS";

class Registry_Server_Default(Enum):
    IP_ADDRESS = "localhost";
    MAX_SERVERS = 3;
    FAILURE = "failure"
    SUCCESS = "success";
    REGISTER = "register";
    GET_SERVER_LIST = "getServerList";
class Server_Default(Enum):
    LEAVE_SERVER = "leaveServer";
    GET_ARTICLES = "getArticles";
    JOIN_SERVER = "joinServer";
    PUBLISH_ARTICLE = "publishArticle";










    


    

        