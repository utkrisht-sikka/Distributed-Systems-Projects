import zmq
import time
import json


class Client:
    def __init__(self, uid):
         
        self.uniqueid = uid
    def GetServerList(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")
        s = "GetServerList " + self.uniqueid
        request = dict()
        request['service'] = "GetServerList"
        request['unique_id'] = self.uniqueid
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        response = json.loads(response)
        print(response['server_addresses'])
        

    def JoinServer(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+str(port))
        request = dict()
        request['service'] = "JoinServer"
        request['unique_id'] = self.uniqueid
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
       
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        response = json.loads(response)
        print("JoinServer reply "+response['status'])
    
    def LeaveServer(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+str(port))
        request = dict()
        request['service'] = "LeaveServer"
        request['unique_id'] = self.uniqueid
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
       
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        response = json.loads(response)
        print("LeaveServer reply "+response['status'])

    def GetArticles(self, port, Type, Author, Published_after):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+str(port))
        request = dict()
        request['service'] = "GetArticles"
        request['unique_id'] = self.uniqueid
        request['Type'] = Type
        request['Author'] = Author
        request['Published_after'] = Published_after
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
        # print("going to sleep")
        # time.sleep(20)
        # print("woken up")
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        print("GetArticles reply "+response)
        response = json.loads(response)
        if(response['status'] == 'FAIL'):
            print(response['status'])
        else:
            cnt=1
            for i in response['articles']:
                print(str(cnt)+")"+i[0])
                print(i[1])
                print(i[2])
                print(i[3])
                cnt+=1
    
    def PublishArticle(self, port, Type, Author, Content):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:"+str(port))
        request = dict()
        request['service'] = "PublishArticle"
        request['unique_id'] = self.uniqueid
        request['Type'] = Type
        request['Author'] = Author
        request['Content'] = Content
        request['date'] = ''
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
         
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        response = json.loads(response)
        print("PublishArticle reply "+response['status'])
         