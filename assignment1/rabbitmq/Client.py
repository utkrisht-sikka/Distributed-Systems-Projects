from datetime import datetime
import json
import uuid
import pika
import dataclasses
from protos import RPC_General,Get_Server_List,Join_Server,Leave_Server,Get_Articles,Publish_Article,Queues,List_Articles,Exchanges,RPC_Server_Response,Registry_Server_Default,Server_Default,RegisterServerRequest,ARTICLE_TYPE
class Client:
    def __init__(self, connection=None,channel=None,client_uuid=None):
        self.uuid = client_uuid if client_uuid is not None else str(uuid.uuid4())
        self.response = None;
    def on_response(self, ch, method, props, body):
        
        self.response = None;status = "NOT_FOR_ME"
        print("I am hungry = {}",self.uuid,props.correlation_id,str(self.uuid)==str(props.correlation_id))
        if str(self.uuid) == str(props.correlation_id):
            print("In on_response method in Client.py props.correlation_id={} uuid={} response={}".format(props.correlation_id,self.uuid,3))
            response = body.decode('utf-8')
            print("Response here is = {}".format(response))
            status = "FOR_ME";
            try:
                final_response = RPC_Server_Response.from_dict(json.loads(response));
            except:
                self.response = json.loads(response);
                return None;

            
            self.response = json.loads(response);
            print("Message Received in client={} status={} server_name={} server_port={} response={}",self.uuid,final_response.status,final_response.server_name,final_response.server_port,final_response.response);
        # return status,response;

        
    def send_general_request(self,message,reply_queue,main_queue,exchange_name,server_name,server_port):
        corr_id = self.uuid
        try:
            print("sending message to queue={} expecting reply at queue={} for server_name={} server_port={}".format(main_queue,reply_queue,server_name,server_port))
            # print("connection={} channel={}".format({"host":self.connection.host,"port":self.connection.port},
            #     {"prefetch_count":self.channel.prefetch_count,"queue":self.channel.queue}))
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=main_queue,
                properties=pika.BasicProperties(
                    reply_to=reply_queue,
                    correlation_id=corr_id,
                ),
                body=message)
            if(reply_queue.find("CLIENT")!=-1):
                self.connection.process_data_events(time_limit=None)
            print("response received in send_general_request for message={} response={}".format(
                message, self.response))
        except Exception as arg:
            print("error occured in  send_general_request for message={} exp={}".format(message, arg))

        return self.response
    def publish_article(self,type,author,content,server_name,server_port):
        if(content=="_" or author=="_" or type=="_"):
            print("Blanks not allowed");
            return "FAILURE";
        if(len(content)>200):
            print("Content length exceeds 200 , The article can't be published on the server")
            return "FAILURE";
        if(type not in [ARTICLE_TYPE.SPORTS.value,ARTICLE_TYPE.POLITICS.value,ARTICLE_TYPE.FASHION.value]):
            print("Invalid Article Type, The article can't be published on the server")
            return "FAILURE";


        current_time = datetime.now().strftime('%d/%m/%y');
        publish_article = Publish_Article(client_uuid=self.uuid,type=type,author=author,content=content,time=current_time,server_name=server_name,server_port=server_port)
        request_msg = RPC_General(Server_Default.PUBLISH_ARTICLE.value,json.dumps(dataclasses.asdict(publish_article)));
        request_json = json.dumps(dataclasses.asdict(request_msg))
        print("sending publish_article request={}".format(request_json));
        response = self.send_general_request(request_json,Queues.CLIENT_RESPONSE_QUEUE.value+self.uuid,server_name+"SREQUEST"+server_port,Exchanges.COMMON_EXCHANGE.value,server_name=server_name,server_port=server_port);
        print("Publish Article request completed with response={} for type={} uuid={} author={}".format(response,type,self.uuid,author));
        
    def get_articles(self,type,author,req_time,server_name,server_port):
        
        get_article = Get_Articles(client_uuid=self.uuid,type=type,author=author,time=req_time)
        request_msg = RPC_General(Server_Default.GET_ARTICLES.value,json.dumps(dataclasses.asdict(get_article)));
        request_json = json.dumps(dataclasses.asdict(request_msg))
        response = self.send_general_request(request_json,Queues.CLIENT_RESPONSE_QUEUE.value+self.uuid,server_name+"SREQUEST"+server_port,Exchanges.COMMON_EXCHANGE.value,server_name=server_name,server_port=server_port);
        print("Get Articles request completed with response={} for type={} uuid={} author={}".format(response,type,self.uuid,author));

    def join_server(self,server_name,server_port):
        join_server = Join_Server(uuid=self.uuid,isServer=False,parent_name=server_name,parent_port=server_port,child_name=None,child_port=None);
        request_msg = RPC_General(Server_Default.JOIN_SERVER.value,json.dumps(dataclasses.asdict(join_server)));
        request_json = json.dumps(dataclasses.asdict(request_msg))
        response = self.send_general_request(request_json,Queues.CLIENT_RESPONSE_QUEUE.value+self.uuid,server_name+"SREQUEST"+server_port,Exchanges.COMMON_EXCHANGE.value,server_name=server_name,server_port=server_port);
        print("Join Server request completed with response={} for uuid={} ".format(response,self.uuid));

    def leave_server(self,server_name,server_port):
        leave_server = Leave_Server(uuid=self.uuid,isServer=False,server_name=server_name,server_port=server_port);
        request_msg = RPC_General(Server_Default.LEAVE_SERVER.value,json.dumps(dataclasses.asdict(leave_server)));
        request_json = json.dumps(dataclasses.asdict(request_msg))
        response = self.send_general_request(request_json,Queues.CLIENT_RESPONSE_QUEUE.value+self.uuid,server_name+"SREQUEST"+server_port,Exchanges.COMMON_EXCHANGE.value,server_name=server_name,server_port=server_port);
        print("Leave Server request completed with response={} for uuid={} ".format(response,self.uuid));
    def getServerList(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message = Registry_Server_Default.GET_SERVER_LIST.value
        try:
            self.channel.basic_publish(
                exchange='registry_server_creation', routing_key='rpc_queue',
                properties=pika.BasicProperties(
                    reply_to='rpc_queue',
                    correlation_id=self.corr_id,
                ), body=str(message))
            self.connection.process_data_events(time_limit=None)
            print("response received in get_server_list for message={} response={}".format(
                message, self.response))
        except Exception as arg:
            print(
                "error occured in  get_server_list for message={} exp={}".format(message, arg))

        return self.response
def getServerNameAndPort():
    server_name = input("Please enter the server_name here : ")
    server_port = input("Please enter the server_port here : ")
    return server_name,server_port;
client = Client();
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',heartbeat=1000))
channel = connection.channel()
channel.basic_qos(prefetch_count=100)
channel.exchange_declare(exchange=Exchanges.COMMON_EXCHANGE.value,
                        exchange_type='direct')

channel.queue_declare(queue=Queues.CLIENT_RESPONSE_QUEUE.value+client.uuid)
# channel.queue_declare(queue = Queues.CLIENT_REQUEST_QUEUE.value)
channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,queue=Queues.CLIENT_RESPONSE_QUEUE.value+client.uuid, routing_key=Queues.CLIENT_RESPONSE_QUEUE.value+client.uuid)
channel.basic_consume(queue=Queues.CLIENT_RESPONSE_QUEUE.value+client.uuid, on_message_callback=client.on_response,auto_ack=True,exclusive=True)
client.connection = connection;client.channel = channel;
print("Welcome to Client client={} Command Line Interface, Press the following keys for doing the given operations".format(client.uuid))
print("1. Join a Server")
print("2. Leave a Server")
print("3. Publish Article")
print("4. Get Articles")
print("5. Join Two Servers Request")
print("6. Get Server List")

set_inp = set([i for i in range(1,7,1)])
count=0;count2=0;count3=0;

print( "--- Press any key other than the above five to break operation ----")
inp = int(input("Please now press the key here : "))
while (inp in set_inp):
    if(inp==1): 
        server_name,server_port = getServerNameAndPort();
        # if(count2%2==0):
        #     server_name,server_port = "Foo","5000"
        #     # article_type,article_author,article_content = "raj","xxx","yyy";
        # else:
        #     server_name,server_port = "Pol","5001"
        #     # article_type,article_author,article_content = "raj","xxx","yyy";
        # count2=1-count2;
        # server_name,server_port = "Foo","5000"
        client.join_server(server_name,server_port);
    elif(inp==2): 
        # print("Please Now enter the server-name and server-port with which you want to connect")
        server_name,server_port = getServerNameAndPort();
        # server_name,server_port = "Foo","5000"
        client.leave_server(server_name,server_port);
    elif(inp==3): 
        server_name,server_port = getServerNameAndPort();
        # if(count%2==0):
        #     # server_name,server_port = "Foo","5000"
        #     article_type,article_author,article_content = "raj","xxx","yyy";
        # else:
        #     # server_name,server_port = "Pol","5001"
        #     article_type,article_author,article_content = "tom","xyz","yyy";

        count=1-count;
        article_type = input("Please enter the type of Article here : ")
        article_author = input("Please enter the name of the author of article here : ")
        article_content = input("Please enter the content of the article here : ")
        
        client.publish_article(article_type,article_author,article_content,server_name,server_port);
        # print()
    elif(inp==4): 
        server_name,server_port = getServerNameAndPort();
        # if(count3%2==0):
        #     server_name,server_port = "Foo","5000"
        #     # article_type,article_author,article_content = "raj","xxx","yyy";
        # else:
        #     server_name,server_port = "Pol","5001"
            # article_type,article_author,article_content = "tom","xyz","yyy";

        count3=1-count3;
        print("Going to request server to show articles for server_name={} server_port={}".format(server_name,server_port))
        # server_name,server_port = "Foo","5000"
        print("Please make sure to add dates in the format dd/mm/yy like 10/02/23")
        article_type_filter = input("Please enter the article_type filter here : ")
        article_author_filter = input("Please enter the name of the author of the articles to be fetched here : ")
        article_time_filter = input("Please enter the timestamp after which articles need to be fetched : ")
        try:
            if(article_time_filter!="_"):
                datetime.strptime(article_time_filter,"%d/%m/%y")
            client.get_articles(article_type_filter,article_author_filter,article_time_filter,server_name,server_port);
        except:
            print("Invalid filter for date format")

        # article_type_filter="_";article_author_filter="_";article_time_filter = "_"
       
    elif(inp==5):
        # server_name,server_port = "Foo","5000"
        # server2_name,server2_port = "Pol","5001"
        print("PLease fill parent_server details")
        server_name,server_port = getServerNameAndPort();
        print("PLease fill child_server details")
        server2_name,server2_port = getServerNameAndPort();
        join_server_req = Join_Server(uuid=client.uuid,child_name=server2_name,child_port=server2_port,parent_name=server_name,parent_port=server_port,isServer=True)
        rpc_req = RPC_General(Server_Default.JOIN_SERVER.value,json.dumps(dataclasses.asdict(join_server_req)))
        message = json.dumps(dataclasses.asdict(rpc_req))
        client.send_general_request(message,server_name+"SRESPONSE"+server2_port,
            server_name+"SREQUEST"+server_port,Exchanges.COMMON_EXCHANGE.value,server_name,server_port)
    elif(inp==6):
        get_server_list = RegisterServerRequest(Registry_Server_Default.GET_SERVER_LIST.value,client.uuid);
        message = json.dumps(dataclasses.asdict(get_server_list))
        client.send_general_request(message,Queues.CLIENT_RESPONSE_QUEUE.value+client.uuid,
            Queues.REGISTRY_SERVER_REQUEST_QUEUE.value,Exchanges.COMMON_EXCHANGE.value,"","")
    inp = int(input("Please now press the key here : "))











    
         