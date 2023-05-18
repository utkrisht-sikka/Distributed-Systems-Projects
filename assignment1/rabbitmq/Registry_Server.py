#!/usr/bin/env python
from enum import Enum
import json
import logging
import pika
from protos import *
server_addresses=[]
MAX_SERVERS = 10;
def process_server_registration(server_name,server_port):
    try:
        if(len(server_addresses)>=MAX_SERVERS): return Registry_Server_Default.FAILURE.name;
        if([server_name,server_port] in server_addresses): return "SUCCESS";
        server_addresses.append([server_name,server_port])
        # final_dict[len(server_addresses)] = server_name+"-"+server_ip;
        print("server registration completed with server_addresses={}",server_addresses);
        return Registry_Server_Default.SUCCESS.name;

    except Exception as arg:
        print("error occured in fib method for body={}",arg)

def getServerList():
    json_object = json.dumps(server_addresses);
    return json_object; 
    



def on_request(ch, method, props, body):
    body = body.decode('utf-8');
    print("request receiver from client={}".format(body))
    json_string = json.loads(body);
    gen_request = RegisterServerRequest.from_dict(json_string);
    request_type = gen_request.request_type;
    # request = gen_request.request;
    if(request_type == Registry_Server_Default.REGISTER.value):
        server_name,server_ip = gen_request.server_name,gen_request.server_port;
        response = process_server_registration(server_name,server_ip);
    elif (request_type == Registry_Server_Default.GET_SERVER_LIST.value):
        client_uuid = gen_request.client_uuid;
        response = getServerList();

    ch.basic_publish(exchange=Exchanges.COMMON_EXCHANGE.value,
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("on_request method execution completed for correlation_id={} response={} props={} request_type={}".format(
        props.correlation_id,response,props,request_type
    ));
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost',heartbeat=1000))


channel = connection.channel()
channel.exchange_declare(exchange=Exchanges.COMMON_EXCHANGE.value,
                         exchange_type='direct')
channel.queue_delete(queue=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value)
channel.queue_declare(queue=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value)
channel.queue_bind(exchange=Exchanges.COMMON_EXCHANGE.value,
                                queue=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value, routing_key=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value)
channel.basic_qos(prefetch_count=100)
channel.basic_consume(queue=Queues.REGISTRY_SERVER_REQUEST_QUEUE.value, on_message_callback=on_request)

print(" [x] Awaiting RPC requests in RegistryServer")
channel.start_consuming()
