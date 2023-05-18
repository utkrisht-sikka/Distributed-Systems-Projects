import time
import grpc
import pubsub_sys_pb2
import pubsub_sys_pb2_grpc
from concurrent import futures
from threading import Thread
import uuid
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

REGISTRY_ADDRESS = "localhost:5555"

TYPE_MAP = {1: "SPORTS", 2: "FASHION", 3:"POLITICS"}

class Client:
    
    def __init__(self, name):
        self.name = name
        self.unique_id = str(uuid.uuid1())
    
    
    def get_server_list(self, stub):
        
        server_list_request = pubsub_sys_pb2.GetServerListRequest()
        server_list_request.client.name = self.name
        server_list_request.client.unique_id = self.unique_id  
        server_list_response = stub.GetServerList(server_list_request)
        return server_list_response

    def join_server(self, stub):
        
        join_server_request = pubsub_sys_pb2.ServerJoinRequest(client_id = self.unique_id)
        join_server_response = stub.JoinServer(join_server_request)
        return join_server_response
    
    def leave_server(self, stub):
        
        leave_server_request = pubsub_sys_pb2.ServerLeaveRequest(client_id = self.unique_id)
        leave_server_response = stub.LeaveServer(leave_server_request)
        return leave_server_response
    
    def get_articles(self, stub, article_type, article_author, article_date):
        
        get_articles_request = pubsub_sys_pb2.GetArticlesRequest()
        get_articles_request.client_id = self.unique_id
        # print(f"here0 : {article_type}")
        # print("here1")
        if(article_type == "SPORTS"):
            # print("here2")
            get_articles_request.article_request.type = pubsub_sys_pb2.SPORTS     
        elif(article_type == "FASHION"):
            # print("here2")
            get_articles_request.article_request.type = pubsub_sys_pb2.FASHION
        elif(article_type == "POLITICS"):
            # print("here3")
            get_articles_request.article_request.type = pubsub_sys_pb2.POLITICS
        elif(article_type == "<blank>"):
            # print("here4")
            get_articles_request.article_request.type = pubsub_sys_pb2.BLANK
        else:
            get_articles_request.article_request.type = pubsub_sys_pb2.NONE
        # get_articles_request.article_request.type = article_type
        get_articles_request.article_request.author = article_author

        if(article_date != "<blank>"):
            try:
                datetime_obj = datetime.strptime(article_date, "%d/%m/%Y")
            except:
                print("Please enter a valid date")
                return
            get_articles_request.article_request.time.FromDatetime(datetime_obj)
        # print(f"final request : {get_articles_request}")
        get_articles_response = stub.GetArticles(get_articles_request)
        return get_articles_response
    
    def publish_article(self, stub, article_type, article_author, article_content):
        
        publish_article_request = pubsub_sys_pb2.PublishArticleRequest()
        publish_article_request.client_id = self.unique_id
        # print("here1")
        # print(f"Here : {pubsub_sys_pb2.SPORTS.name}, {pubsub_sys_pb2.SPORTS.value}")
        
        if(article_type == "SPORTS"):
            # print("here2")
            publish_article_request.article.type = pubsub_sys_pb2.SPORTS     
        elif(article_type == "FASHION"):
            publish_article_request.article.type = pubsub_sys_pb2.FASHION
        elif(article_type == "POLITICS"):
            publish_article_request.article.type = pubsub_sys_pb2.POLITICS
        elif(article_type == "<blank>"):
            publish_article_request.article.type = pubsub_sys_pb2.BLANK
        else:
            publish_article_request.article.type = pubsub_sys_pb2.NONE            
        publish_article_request.article.author = article_author
        publish_article_request.article.content = article_content
        # print(f"Request : {publish_article_request}")
        publish_article_response = stub.PublishArticle(publish_article_request)
        return publish_article_response

if __name__ == "__main__":
    
    client_name = input("Enter a client name : ")
    client_object = Client(client_name)
    # try:
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        registry_stub = pubsub_sys_pb2_grpc.RegistryServiceStub(channel)
        while True:
            
            print("----------- Client Requests -----------")
            print("1 -> Get servers list from registry server\n2 -> Join a server\n3 -> Leave a server\n4 -> Get articles from a server\n5 -> Publish article to a server\n")
            print("---------------------------------------\n")
            request_input = input(">> Enter the option number : ")
            
            
            if request_input == '1':
                get_server_list_response = client_object.get_server_list(registry_stub)
                print("List of servers received from registry:")
                if(len(get_server_list_response.server_list) == 0):
                    print("[Empty list]")
                else:
                    for server_obj in get_server_list_response.server_list:
                        print(f"-> {server_obj.name} - {server_obj.address}")
            
            if request_input == '2':
                input_server_address = input("Enter server address : ")
                try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = pubsub_sys_pb2_grpc.ServerServiceStub(channel)
                        join_server_response = client_object.join_server(server_stub)
                        print(f"[{join_server_response.status}] : {join_server_response.message}")
                except:
                    print("Could not connect to the server. Please check the server address.")
            
            if request_input == '3':
                input_server_address = input("Enter server address : ")
                try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = pubsub_sys_pb2_grpc.ServerServiceStub(channel)
                        leave_server_response = client_object.leave_server(server_stub)
                        print(f"[{leave_server_response.status}] : {leave_server_response.message}")
                except:
                    print("Could not connect to the server. Please check the server address.")
            
            if request_input == '4':
                input_server_address = input("Enter server address : ")
                print("Enter the tags to filter articles")
                input_article_type = input("Enter article type : ")
                input_article_author = input("Enter article author : ")
                input_article_date = input("Enter article date : ")
                # try:
                with grpc.insecure_channel(input_server_address) as channel:
                    server_stub = pubsub_sys_pb2_grpc.ServerServiceStub(channel)
                    get_articles_response = client_object.get_articles(server_stub, input_article_type, input_article_author, input_article_date)
                    print(f"[{get_articles_response.status}] : {get_articles_response.message}")
                    if(len(get_articles_response.articles) == 0):
                        print("[Empty list]")
                    else:
                        for num, article in enumerate(get_articles_response.articles):
                            print(f"\n===== [Article {num + 1}] =====")
                            print(f"->Type : {TYPE_MAP[article.type]}")
                            print(f"->Author : {article.author}")
                            article_timestamp = article.time
                            article_datetime = article_timestamp.ToDatetime()
                            article_date = article_datetime.strftime("%d/%m/%Y")
                            print(f"->Date : {article_date}")
                            print(f"->Content : {article.content}")                    
                # except:
                #     print("Could not connect to the server. Please check the server address.")
                    
            if request_input == '5':
                input_server_address = input("Enter server address : ")
                print("Enter article details :")
                input_article_type = input("Enter article type : ")
                input_article_author = input("Enter article author : ")
                input_article_content = input("Enter article content : ")
                
                # if(input_article_type == "SPORTS"):
                #     type_value = pubsub_sys_pb2.ArticleType.SPORTS
                # elif(input_article_type == "FASHION"):
                #     type_value = pubsub_sys_pb2.ArticleType.FASHION
                # elif(input_article_type == "POLITICS"):
                #     type_value = pubsub_sys_pb2.ArticleType.POLITICS
                
                # try:
                with grpc.insecure_channel(input_server_address) as channel:
                    server_stub = pubsub_sys_pb2_grpc.ServerServiceStub(channel)
                    publish_article_response = client_object.publish_article(stub=server_stub, article_type=input_article_type, 
                                                                                article_author=input_article_author,article_content=input_article_content)
                    print(f"[{publish_article_response.status}] : {publish_article_response.message}")
                # except:
                #     print("Could not connect to the server. Please check the server address.")
            
                        
            print("\n\n---------------------------------------\n\n")    
    # except:
    #     print("COULD NOT CONNECT TO REGISTRY SERVER. PLEASE TRY AGAIN. [client]")
            
            