#!/usr/bin/env python
from copy import deepcopy
from datetime import datetime
from enum import Enum
import json
import pika
import uuid
import logging
import dataclasses
from protos import RPC_General,Get_Server_List,Join_Server,Leave_Server,Get_Articles,Publish_Article,Article,List_Articles,Queues,Exchanges,RPC_Server_Response, RegisterServerRequest,Registry_Server_Default,Server_Default

class Server(object):
    def send_general_request(self,message,reply_queue,main_queue,exchange_name,server_ip,server_port,flag):
        # corr_id = str(uuid.uuid4())
        try:
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=main_queue,
                properties=pika.BasicProperties(
                    reply_to=reply_queue,
                    correlation_id=self.corr_id
                    # content_type='application/json'
                ),
                body=message)
            if(flag):
                self.connection.process_data_events(time_limit=None)
            print("response received in send_general_request for message={} response={}".format(
                message, self.response))
        except Exception as arg:
            print("error occured in  send_general_request for message={}".format(message, arg))

        return self.response
    def __init__(self, name, port,MAXCLIENTS = 10):
        # connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(host='localhost'))
        self.name, self.port = name, port
        # channel = self.connection.channel()
        self.corr_id = str(uuid.uuid4());
        self.CLIENTELE = []
        self.SERVERELE = []
        self.MAXCLIENTS = MAXCLIENTS;
        self.articles = [];
        self.articles_uuid=set();
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',heartbeat=1000))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=Exchanges.COMMON_EXCHANGE.value,
                                exchange_type='direct')

        print("Now declaring queues in Server.py")
        try:
            self.channel.queue_delete(queue=self.name+"SREQUEST"+self.port);
            self.channel.queue_delete(queue=self.name+"SRESPONSE"+self.port);
            self.channel.queue_delete(queue=self.name+"FREQUEST"+self.port);
            self.channel.queue_delete(queue = self.name+"FRESPONSE"+self.port);
        except:
            rp=2;
        self.channel.queue_declare(queue=self.name+"SREQUEST"+self.port, durable=False)
        self.channel.queue_declare(queue=self.name+"SRESPONSE"+self.port, durable=False)
        self.channel.queue_declare(queue=self.name+"FREQUEST"+self.port, durable=False)
        self.channel.queue_declare(queue = self.name+"FRESPONSE"+self.port, durable=False)
        self.channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=self.name+"SREQUEST"+self.port, routing_key=self.name+"SREQUEST"+self.port)
        self.channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=self.name+"SRESPONSE"+self.port, routing_key=self.name+"SRESPONSE"+self.port)
        self.channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=self.name+"FREQUEST"+self.port, routing_key=self.name+"FREQUEST"+self.port)
        self.channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=self.name+"FRESPONSE"+self.port, routing_key=self.name+"FRESPONSE"+self.port)
        self.channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value, routing_key=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value)
        
        self.channel.basic_qos(prefetch_count=100)
        self.channel.basic_consume(queue=self.name+"SREQUEST"+self.port, on_message_callback=self.on_server_request,consumer_tag=self.name+" "+self.name+"SREQUEST"+self.port)
        self.channel.basic_consume(queue=self.name+"SRESPONSE"+self.port, on_message_callback=self.on_server_response,consumer_tag=self.name+" "+self.name+"SRESPONSE"+self.port,auto_ack=True)
        self.channel.basic_consume(queue=self.name+"FREQUEST"+self.port, on_message_callback=self.on_fetch_request,consumer_tag=self.name+" "+self.name+"FREQUEST"+self.port)
        self.channel.basic_consume(queue=self.name+"FRESPONSE"+self.port, on_message_callback=self.on_fetch_response,consumer_tag=self.name+" "+self.name+"FRESPONSE"+self.port,auto_ack=True)
        self.response = None
        self.Register();
        # self.channel.queue_bind(exchange=Exchanges.SERVER_EXCHANGE.value,
        #                         queue=Queues.CLIENT_RESPONSE_QUEUE.value+self.port, routing_key=Queues.CLIENT_RESPONSE_QUEUE.value+self.port)
                
        # channel.basic_consume(
        #     queue=self.callback_queue,
        #     on_message_callback=self.on_response,
        #     auto_ack=True)

        print("Now setting basic_consume in Server.py")

        
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()
        
        

    # def on_response(self, ch, method, props, body):
    #     print("In on_response method in server.py")
    #     if self.corr_id == props.correlation_id:
    #         response = body.decode()
    
    def on_server_response(self, ch, method, props, body):
        print("In on_server_response method in server.py")
        response = None;status = "NOT_FOR_ME"
        if self.corr_id == props.correlation_id:
            response = body.decode('utf-8')
            try:
                final_response = RPC_Server_Response.from_dict(json.loads(response));
                self.response = final_response;
            except:
                final_response = response;
                self.response = final_response;
                print("Response is not of type RPC_Server_Response")
                return None;
            status = "FOR_ME";
            print("Message Received in JoinServer response child_server={} child_port={} status={} server_name={} server_port={} response={}",self.name,self.port,final_response.status,final_response.server_name,final_response.server_port,final_response.response);

    def Register(self):
        self.response = None
        # corr_id = str(uuid.uuid4())
        message = RegisterServerRequest(Registry_Server_Default.REGISTER.value,"",self.name,self.port);
        final_message = json.dumps(dataclasses.asdict(message));
        self.send_general_request(final_message,self.name+"SRESPONSE"+self.port,Queues.REGISTRY_SERVER_REQUEST_QUEUE.value,Exchanges.COMMON_EXCHANGE.value,server_name,server_port,True)
        # return self.response

    
    def send_response(self,ch,method,props,response,req_type):
        # send response to client or server for joinServer or leaveServer or any method
        print("Sending response to Client.py with routing_key={} correlation_id={}",props.reply_to,props.correlation_id)
        ch.basic_publish(exchange=Exchanges.COMMON_EXCHANGE.value,
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = props.correlation_id),
                        body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("on_request method execution completed for correlation_id={} response={} props={} method={} request_type={}".format(
            props.correlation_id,response,props,method,req_type
        ));
    def on_fetch_request(self,ch, method, props, body):
        try:
            body = body.decode(encoding = 'utf-8'); #convert bytes to string
        except Exception as arg:
            print("Body is of str type not bytes")
        print("request receiver in on_fetch_request with body={}".format(body))
        json_string = json.loads(body);
        # gen_request = RPC_General.from_dict(json_string);
        # req_type = gen_request.req_type;
        dummy_articles = List_Articles.from_dict(json_string);
        server_names = dummy_articles.server_names;
        server_ports = dummy_articles.server_ports;
        articles = dummy_articles.articles;
        if ((self.name in server_names) and (self.port in server_ports)):
            print("This server with name={} port={} has already been processed for fetching articles".format(self.name,self.port))
            return "FAILURE",None;
        else:
            prev_length = len(self.articles);
            server_names.append(self.name);
            server_ports.append(self.port);
            for article in articles:
                if(article.uuid not in self.articles_uuid):
                    self.articles_uuid.add(article.uuid);
                    self.articles.append(article);
                    print("Adding article with details={} in server={} server_names={} server_ports={}".format(article.type+" "+article.content,self.name,server_names,server_ports));
            new_length = len(self.articles);
            if(new_length>prev_length):
                # print("Iterating on children servers and currently in server_name={} server_port={}".format(server[0],server[1]));
                new_list = List_Articles(self.articles,server_names,server_ports)
                json_articles_list = json.dumps(dataclasses.asdict(new_list));
                for server in self.SERVERELE:
                    print("Iterating on children servers and currently in server_name={} server_port={}".format(server[0],server[1]))
                    self.send_general_request(json_articles_list,self.name+"FRESPONSE"+self.port,server[0]+"FREQUEST"+server[1],Exchanges.COMMON_EXCHANGE.value,server[0],server[1],False)
                print("Method execution completed here")
            
            return "SUCCESS",None;
                    


            

        
        return None;
    def on_fetch_response(self,ch, method, props, body):
        body = body.decode(encoding = 'utf-8'); #convert bytes to string

       
        json_string = json.loads(body);
        print("response received to server for fetch_response={}".format(body))
        
        
    def validateIPandPort(self,request):
        try:
            if((request.get("parent_name")==self.name and request.get("parent_port")==self.port) or (request.get("server_name")==self.name and request.get("server_port")==self.port)):
                return "SUCCESS";
            elif("parent_name" not in request) and ("server_name" not in request):
                return "SUCCESS";
        except Exception as arg:
            print("error occured in validateIPandPort for request={}",request,arg);
        return "FAILURE";
    # methods for receiving requests on server
    def on_server_request(self,ch, method, props, body):
        # print("hello from here")
        body = body.decode(encoding = 'utf-8'); #convert bytes to string
        
        json_string = json.loads(body);
        gen_request = RPC_General.from_dict(json_string);
        req_type = gen_request.req_type;
        request = gen_request.request;
        status = self.validateIPandPort(request);
        if(status=="FAILURE"): return "FAILURE";

        print("In onRequest method in Server class for req_type={} request={}".format(gen_request.req_type,gen_request.request))
        
        if(req_type == Server_Default.JOIN_SERVER.value):
            join_server_req = Join_Server.from_dict(request);
            status,response = self.processServerRegistration(join_server_req);
        elif (req_type == Server_Default.LEAVE_SERVER.value):
            leave_server_req = Leave_Server.from_dict(request);
            status,response = self.processServerRemoval(leave_server_req);
        elif (req_type == Server_Default.GET_ARTICLES.value):
            get_articles_request = Get_Articles.from_dict(request);
            status,response = self.getArticleList(get_articles_request);
        elif(req_type == Server_Default.PUBLISH_ARTICLE.value):
            publish_articles_request = Publish_Article.from_dict(request);
            status,response = self.publishArticle(publish_articles_request);
        response = "EMPTY" if response is None else response;
        final_response = RPC_Server_Response(status,response,self.name,self.port)
        dump_response = json.dumps(dataclasses.asdict(final_response))
        self.send_response(ch,method,props,dump_response,req_type)
        print("clientele={} serverle={} articles={}".format(self.CLIENTELE,self.SERVERELE,len(self.articles)));
        
    def processServerRegistration(self,join_server_req: Join_Server):
        response = None;
        if(len(self.CLIENTELE)+len(self.SERVERELE)==self.MAXCLIENTS):
            print("The server has connected to maximum clients with which it can connect = {}".format(self.MAXCLIENTS))
            return "FAILURE",None;
        if(join_server_req.isServer == False):
            uuid = join_server_req.uuid;
            if(uuid in self.CLIENTELE):
                print("The client with uuid={} has already connected to the given server with name={} port={} ".format(uuid,self.name,self.port))
                return "FAILURE",None;
            else:
                self.CLIENTELE.append(uuid);
                print("The client with uuid={} is getting connected to the given server with name={} port={} ".format(uuid,self.name,self.port))
                return "SUCCESS",None;

        elif(join_server_req.isServer == True):
            #server wants to join in this case
            child_name = join_server_req.child_name;
            child_port = join_server_req.child_port;
            server = [child_name,child_port];
            if( server in self.SERVERELE):
                print("The server with server_ip={} server_port={} has already connected to the given server with name={} port={} ".format(child_name,child_port,self.name,self.port))
                return "FAILURE",None;
            else:
                print("Appending server to serverele");
                self.SERVERELE.append(server);
                parent_articles = deepcopy(self.articles);
                list_articles = List_Articles(articles=parent_articles,server_names=[self.name],server_ports=[self.port])
                json_list_articles = json.dumps(dataclasses.asdict(list_articles));
                print("Sending request to process articles message={} response_queue={} main_queue={} child_name={} child_port={} parent_name={} parent_port={}".format(json_list_articles,self.name+"SRESPONSE"+self.port,child_name+"FREQUEST"+child_port,child_name,child_port,self.name,self.port));
                self.send_general_request(json_list_articles,self.name+"SRESPONSE"+self.port,child_name+"FREQUEST"+child_port,Exchanges.COMMON_EXCHANGE.value,child_name,child_port,False);
                return "SUCCESS",None

            
            
        return "FAILURE",None;
    
    def processServerRemoval(self,leave_server_req: Leave_Server):
        status = "FAILURE";
        
        if(leave_server_req.isServer == False):
            uuid = leave_server_req.uuid;
            if(uuid not in self.CLIENTELE):
                print("The client with uuid={} has not connected to the given server with name={} port={} ".format(uuid,self.name,self.port))
                status =  "FAILURE";
            else:
                self.CLIENTELE.remove(uuid);
                print("The client with uuid={} has left the given server with name={} port={} ".format(uuid,self.name,self.port))
                status =  "SUCCESS";
        return status,None;
    def getTime(self,date_str):
        return datetime.strptime(date_str,"%d/%m/%y")
    def getArticleList(self,get_articles_request: Get_Articles):
        if(get_articles_request.client_uuid not in self.CLIENTELE):
            print("Client with uuid={} is not part of Clientele for server_name={} server_port={}".format(get_articles_request.client_uuid,self.name,self.port))

            return "FAILURE",None;
        filter_author=get_articles_request.author;
        filter_time=get_articles_request.time;
        filter_type=get_articles_request.type;

        data = self.articles;
        isAuthor = True;isTime=True;isType=True;
        try:
            if(filter_author.strip()=="_"): isAuthor = False;
            if(filter_type.strip()=="_"): isType = False;
            if(filter_time.strip()=="_"): isTime = False;
        except Exception as arg:
            isAuthor = True;isTime=True;isType=True;
        filtered_whole = self.articles;
        if(isAuthor): filtered_whole = [x for x in filtered_whole if x.author==filter_author]
        if(isType): filtered_whole = [x for x in filtered_whole if x.type==filter_type]
        if(isTime): filtered_whole = [x for x in filtered_whole if self.getTime(x.time)>=self.getTime(filter_time)]
        filtered_whole = [json.dumps(dataclasses.asdict(x)) for x in filtered_whole]
        print("articles to be sent after filtering={}".format(filtered_whole))
        return "SUCCESS",json.dumps(filtered_whole);
    
    def publishArticle(self,publish_articles_request:Publish_Article):
        if(publish_articles_request.author == None or publish_articles_request.content == None or publish_articles_request.time==None
                or publish_articles_request.type == None or publish_articles_request.client_uuid == None or 
                (publish_articles_request.client_uuid not in self.CLIENTELE)):
                print("Article can't be published for publish_articles_request={} for server_name={} server_port={}".format(publish_articles_request,self.name,self.port));
                return "FAILURE",None;
        
        current_time = datetime.now().strftime('%d/%m/%y')
        article = Article(publish_articles_request.type,publish_articles_request.author,current_time,publish_articles_request.content,str(uuid.uuid4()))    
        articles_before = deepcopy(self.articles);
        articles_before.append(article);
        list_articles = List_Articles(articles=articles_before,server_names=[],server_ports=[])
        json_list_articles = json.dumps(dataclasses.asdict(list_articles));
        print("Sending message to fetch_request_queue for articles={}".format(json_list_articles))
        # self.send_general_request(json_list_articles,self.name+"SRESPONSE"+self.port,self.name+"FREQUEST"+self.port,Exchanges.SERVER_EXCHANGE.value,self.name,self.port);
        self.on_fetch_request(self.channel,None,None,json_list_articles);

        # write code for sending aticles from one server to other using queue.
        return "SUCCESS",None;
    def joinServer(self,parent_name,parent_port):
        join_server_request = Join_Server(child_name=self.name,child_port=self.port,parent_name=parent_name,parent_port=parent_port)
        message = json.dumps(dataclasses.asdict(join_server_request));
        self.send_general_request(message,self.name+"SRESPONSE"+self.port,self.name+"SREQUEST"+self.port,parent_name,parent_port);
        print("Request sent to join server for child_name={} child_port={} parent_name={} parent_port={}",self.name,self.port,parent_name,parent_port)
# server_name,server_port = input("Please enter Server name and port in space separated manner : \n").split();
server_name = input("Enter server name here :   ")
server_port = input("Enter server port here :   ")

server1 = Server(server_name,server_port);

        
        
    



