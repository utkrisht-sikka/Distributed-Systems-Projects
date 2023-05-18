import time
import zmq
import json


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
server_addresses = []

MAXSERVERS = 10
def RegisterServer(socket, message):
    print("JOIN REQUEST FROM "+message['unique_id'])
    if(len(server_addresses) < MAXSERVERS):
         
        server_addresses.append(message['ip_port'])
        # time.sleep(20)
        response = dict()
        response['status'] = 'SUCCESS'
        tosend = json.dumps(response)
        socket.send(tosend.encode('ASCII'))
    else:
        response = dict()
        response['status'] = 'FAIL'
        tosend = json.dumps(response)
        socket.send(tosend.encode('ASCII'))
def GetServerList(socket, message):

    print("SERVER LIST REQUEST FROM "+message['unique_id'])
    response = dict()
    response['server_addresses'] = server_addresses
    tosend = json.dumps(response)
    socket.send(tosend.encode('ASCII'))
    



while True:
    message = socket.recv()
    message = message.decode('ASCII')
    
    print("Received request: %s" % message)
    message = json.loads(message)
    if(message['service'] == "Register"):
        RegisterServer(socket, message)
    elif(message['service'] == "GetServerList"):
        GetServerList(socket, message)
    else:
        socket.send(b"FAIL")
    time.sleep(1)