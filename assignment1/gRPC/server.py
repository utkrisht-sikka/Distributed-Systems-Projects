import time
import grpc
import pubsub_sys_pb2
import pubsub_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
from datetime import date
from article import Article, ALLOWED_TYPES
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

REGISTRY_ADDRESS = "localhost:5555"

class Server(pubsub_sys_pb2_grpc.ServerServiceServicer):
    
    def __init__(self, ip, port, name, max_clients=5):
        self.address = ip + ":" + str(port)
        self.name = name
        self.max_clients = max_clients
        self.lock = Lock()
        self.clientele = []
        self.articles = []
    
    def register_server(self, stub):
        registration_request = pubsub_sys_pb2.RegisterServerRequest(
            name = self.name,
            address = self.address
        )
        registration_response = stub.RegisterServer(registration_request)
        return registration_response
    
    def JoinServer(self, request, context):
        
        client_id = request.client_id
        print(f"\nJOIN REQUEST FROM {client_id}")
        
        if(client_id in self.clientele):
            # Here, we assume that if the client is already a part of the server and still sends a join request, then we still return a SUCCESS response as the client has effectively "JOINED" the server
            print("  |-> Client already a part of server")
            return pubsub_sys_pb2.ServerJoinResponse(
                status="SUCCESS",
                message="Client is already a part of this server"
            )
        
        if(len(self.clientele) < max_clients):
            try:
                self.clientele.append(client_id)
                print(f"  |-> Successfully joined\n  |-> Clients: {self.clientele}")
                return pubsub_sys_pb2.ServerJoinResponse(
                    status="SUCCESS",
                    message="Client successfully added to server"
                )
            except:
                print(f" |-> Failed to add client to server")
                return pubsub_sys_pb2.ServerJoinResponse(
                    status="FAIL",
                    message="Failed to add client to server"
                )
        else:
            print(f" |-> Failed to add client to server, max no. of clients reached")
            return pubsub_sys_pb2.ServerJoinResponse(
                status="FAIL",
                message="Failed to add client to server [max no. of clients reached]"
            )

    def LeaveServer(self, request, context):
        
        client_id = request.client_id
        print(f"\nLEAVE REQUEST FROM {client_id}")
        
        if(client_id not in self.clientele):
            # Here, we assume that if the client is already not a part of the server and still sends a leave request, then we still return a SUCCESS response as the client has effectively "LEFT" the server
            print("  |-> Client already not a part of server")
            return pubsub_sys_pb2.ServerLeaveResponse(
                status="SUCCESS",
                message="Client is already not a part of this server"
            )
        
        try:
            self.clientele.remove(client_id)
            print(f"  |-> Successfully removed\n  |-> Clients: {self.clientele}")
            return pubsub_sys_pb2.ServerLeaveResponse(
                status="SUCCESS",
                message="Client successfully removed from server"
            )
        except:
            print(f" |-> Failed to remove client from server")
            return pubsub_sys_pb2.ServerLeaveResponse(
                status="FAIL",
                message="Failed to remove client from server"
            )
           
    def GetArticles(self, request, context):
        
        print(f"\nARTICLES REQUEST FROM {request.client_id} FOR [{request.article_request.type},{request.article_request.author},{request.article_request.time}]") 
        self.lock.acquire()
        if(request.client_id in self.clientele):
            type_tag = request.article_request.type
            author_tag = request.article_request.author
            time_tag = request.article_request.time
            
            if(type_tag != 4 and (type_tag not in [1, 2, 3])):
                get_articles_response = pubsub_sys_pb2.GetArticlesResponse()
                get_articles_response.status = "FAIL"
                get_articles_response.message = "Article type not valid. (ALLOWED_TYPES = [SPORTS, FASHION, POLITICS])"
                self.lock.release()
                print(" |-> Failed to fetch articles, Invalid article type")
                return get_articles_response
            else:
                get_articles_response = pubsub_sys_pb2.GetArticlesResponse()
                filtered_articles = Article.filter_by_date(Article.filter_by_author(Article.filter_by_type(self.articles, type_tag), author_tag), time_tag)
                for article in filtered_articles:
                    article_item = get_articles_response.articles.add()
                    article_item.type = article.type
                    article_item.author = article.author
                    article_datetime = article.time.ToDatetime()
                    article_item.time.FromDatetime(article_datetime)
                    article_item.content = article.content
                
                get_articles_response.status = "SUCCESS"
                get_articles_response.message = "Articles successfully fetched."
                
                self.lock.release()
                print("  |-> Articles fetched successfully")
                return get_articles_response    
            
        else:
            get_articles_response = pubsub_sys_pb2.GetArticlesResponse()
            get_articles_response.status = "FAIL"
            get_articles_response.message = "Client not a part of this server"
            self.lock.release()
            print("  |-> Failed to fetch articles, Client not a part of this server")
            return get_articles_response
            
            
    
    def PublishArticle(self, request, context):
        
        print(f"\nARTICLE PUBLISH FROM {request.client_id}")
        print(f"Article content : {request.article}")
        
        self.lock.acquire()
        received_timestamp = Timestamp()
        received_timestamp.FromDatetime(datetime.now())
           
        if(request.client_id in self.clientele):
            article_type = request.article.type
            article_author = request.article.author
            article_content = request.article.content
            article_time = received_timestamp
            # print(f"Article type : {request.article.type}")
            if(article_type == 4 or article_author == "<blank>" or article_content == "<blank>"):
                self.lock.release()
                print("  |-> Failed to publish article, no fields can be empty")
                return pubsub_sys_pb2.PublishArticleResponse(
                    status="FAIL",
                    message="No field can be empty."
                )
            
            if(article_type in [1, 2, 3]):
                if(len(article_content) <= 200):
                    article_object = Article(type=article_type, author=article_author, content=article_content, time=article_time, client_id=request.client_id, server_address=self.address)
                    self.articles.append(article_object)
                    self.lock.release()
                    print("  |-> Articles published successfully")
                    return pubsub_sys_pb2.PublishArticleResponse(
                        status="SUCCESS",
                        message="Article published successfully"
                    )
                else:
                    self.lock.release()
                    print("  |-> Failed to publish article, content length too long (>200 characters)")
                    return pubsub_sys_pb2.PublishArticleResponse(
                        status="FAIL",
                        message="Article content length too long (>200 characters)"
                    )
            else:
                self.lock.release()
                print(" |-> Failed to publish articles, Invalid article type")
                return pubsub_sys_pb2.PublishArticleResponse(
                    status="FAIL",
                    message="Article type not allowed (ALLOWED_TYPES = [SPORTS, FASHION, POLITICS])"
                )
            
        else:
            self.lock.release()
            print("  |-> Failed to publish article, client not a part of this server")
            return pubsub_sys_pb2.PublishArticleResponse(
                status="FAIL",
                message="Client not a part of server"
            )

if __name__ == "__main__":
    
    print("Please enter the details of the server")
    ip = input("IP : ")
    port = input("Port : ")
    name = input("Name : ")
    max_clients = int(input("Max number of clients : "))
    server_object = Server(ip, port, name, max_clients)
    
    if(server_object.address == "localhost:5555"):
        print("Address already taken by registry server")
    
    else:
        print(f"---> DEPLOYING SERVER [{server_object.name}]:{server_object.address}")
        # try:
        with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
            registry_stub = pubsub_sys_pb2_grpc.RegistryServiceStub(channel)
            registration_response = server_object.register_server(registry_stub)
            print(f"Server registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_server = grpc.server(futures.ThreadPoolExecutor())
                pubsub_sys_pb2_grpc.add_ServerServiceServicer_to_server(server_object, grpc_server)
                grpc_server.add_insecure_port(server_object.address)
                print(f"\n\n-------- Starting server : {server_object.name}-{server_object.address} --------\n")
                grpc_server.start()
                grpc_server.wait_for_termination()
            else:
                print(f" -------- Failed to start server : {server_object.name}-{server_object.address} --------")
        # except:
        #     print("COULD NOT CONNECT TO REGISTRY SERVER. PLEASE TRY AGAIN.")