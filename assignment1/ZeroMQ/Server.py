import time
import zmq
from datetime import date
from threading import Lock
import uuid
import json

MAXCLIENTS = 10

class Server:
    def __init__(self, port, port2, uid, name):
        context = zmq.Context()
        self.socket_talkto_rs = context.socket(zmq.REQ)
        self.socket_talkto_c = context.socket(zmq.REP)
        self.socket_talkto_parent = context.socket(zmq.SUB)
        self.socket_talkto_child = context.socket(zmq.PUB)
        self.socket_talkto_child.bind("tcp://*:"+str(port2))
        self.socket_talkto_c.bind("tcp://*:"+str(port))
        self.CLIENTELE = []
        self.port = port
        self.articles = []
        self.articles_id = set()
        self.lock = Lock()
        self.uniqueid = uid
        self.Register(name)
         

    def Register(self, name):
        self.socket_talkto_rs.connect("tcp://localhost:5555")
        
        request = dict()
        request['service'] = "Register"
        request['name'] = name
        request['ip_port'] = "localhost:"+str(self.port)
        request['unique_id'] = self.uniqueid
        tosend = json.dumps(request)
        self.socket_talkto_rs.send(tosend.encode('ASCII'))
        response = self.socket_talkto_rs.recv()
        response = response.decode('ASCII')
        response = json.loads(response)
        print("Register reply "+response['status'])

    def JoinServer(self, message):
        
        print("JOIN REQUEST FROM "+message['unique_id'])
        response = dict()       
        if((len(self.CLIENTELE) < MAXCLIENTS) and (message['unique_id'] not in self.CLIENTELE)):
            self.CLIENTELE.append(message['unique_id'])
            response['status'] = 'SUCCESS'
        else:
            response['status'] = 'FAIL'
        tosend = json.dumps(response)
        self.socket_talkto_c.send(tosend.encode('ASCII'))
    
    def LeaveServer(self, message):
        print("LEAVE REQUEST FROM "+message['unique_id'])
        response = dict()
        if( message['unique_id'] in  self.CLIENTELE):
            self.CLIENTELE.remove(message['unique_id'])
            response['status'] = 'SUCCESS'
        else:
            response['status'] = 'FAIL'
        tosend = json.dumps(response)
        self.socket_talkto_c.send(tosend.encode('ASCII'))

    def check_type(self, Type, articles):
        if(Type == ''):
            return articles

        li = []
        for i in articles:
            if i[0]==Type:
                li.append(i)
        return li

    def check_time(self, time, articles):
        if(time == ''):
            return articles
        day, month, year = time.split("/")
        c = date(int(year), int(month), int(day))
        li = []
        for i in articles:
            if i[2] >= c:
                li.append(i)
        return li

    def check_author(self, author, articles):
        if(author == ''):
            return articles

        li = []
        for i in articles:
            if i[1] == author:
                li.append(i)
        return li
 
    def processdate(self, articles):
        newlist = []
        for i in range(len(articles)):
            article = articles[i]
            a = str(article[2])
            year, month, day  = a.split("-")
            article = (article[0], article[1], day+"/"+month+"/"+year, article[3], article[4])
            newlist.append(article)
        
        return newlist

    def GetArticlesforServer(self, message):
        self.lock.acquire()
        response = dict()
        print("ARTICLES REQUEST FROM "+message['unique_id'])
        print("FOR %s,%s,%s"%(message['Type'], message['Author'], message['Published_after']))
       
        by_type = self.check_type(message['Type'], self.articles)  
        by_time = self.check_time( message['Published_after'], by_type)
        by_author = self.check_author( message['Author'], by_time)
        by_author = self.processdate(by_author)
        # print("going to sleep")
        # time.sleep(5)
        print("by_author")
        print(by_author)
        
        response['articles'] = by_author
        response['status'] = 'SUCCESS'
    
        # a=self.socket_talkto_c.send(tosend.encode('ASCII'), copy=False, track=True)
        # print("returns")
        # print(a.done)

        

        tosend = json.dumps(response)
        self.socket_talkto_c.send(tosend.encode('ASCII'))
        self.lock.release()



    def GetArticles(self, message):
        self.lock.acquire()
        response = dict()
        print("ARTICLES REQUEST FROM "+message['unique_id'])
        print("FOR %s,%s,%s"%(message['Type'], message['Author'], message['Published_after']))
        if( message['unique_id'] in  self.CLIENTELE):
            by_type = self.check_type(message['Type'], self.articles)  
            by_time = self.check_time( message['Published_after'], by_type)
            by_author = self.check_author( message['Author'], by_time)
            by_author = self.processdate(by_author)
            # print("going to sleep")
            # time.sleep(5)
            # print("woken up")
            
            response['articles'] = by_author
            response['status'] = 'SUCCESS'
       
            # a=self.socket_talkto_c.send(tosend.encode('ASCII'), copy=False, track=True)
            # print("returns")
            # print(a.done)

        else:
            response['articles'] = []
            response['status'] = 'FAIL'
        

        tosend = json.dumps(response)
        self.socket_talkto_c.send(tosend.encode('ASCII'))
        self.lock.release()

    def PublishArticle(self, message):
        self.lock.acquire()
        response = dict()
        print("ARTICLES PUBLISH FROM "+message['unique_id'])
        if( message['unique_id'] in  self.CLIENTELE):
            if(message['Type'] not in ["SPORTS", "FASHION", "POLITICS"]):
                response['status'] = 'FAIL'
            elif(len(message['Content']) > 200):
                response['status'] = 'FAIL'
            elif(message['date'] != ''):
                response['status'] = 'FAIL'
            else:
                 
                article_id = str(uuid.uuid1())

                self.articles.append((message['Type'], message['Author'], date.today(), message['Content'], article_id))
                self.articles_id.add(article_id)
                message['article_id'] = article_id
                message['date'] = str(date.today())
                tosend = json.dumps(message)
                self.socket_talkto_child.send(tosend.encode("ASCII"))
                response['status'] = 'SUCCESS'
        else:
            response['status'] = 'FAIL'
        tosend = json.dumps(response)
        self.socket_talkto_c.send(tosend.encode('ASCII'))
        self.lock.release()

    def Run(self):
        while True:
            message = self.socket_talkto_c.recv()
            message = message.decode('ASCII')
            print("Received request: %s" % message)
            message = json.loads(message)
            
            if(message['service'] == "JoinServer"):
                self.JoinServer(message)
            elif(message['service'] == "LeaveServer"):
                self.LeaveServer(message)
            elif(message['service'] == "GetArticles"):
                self.GetArticles(message)
            elif(message['service'] == "PublishArticle"):
                self.PublishArticle(message)
            elif(message['service'] == "GetArticlesforServer"): 
                self.GetArticlesforServer(message)
            else:
                response = dict()
                response['status'] = 'FAIL'
                tosend = json.dumps(response)
                self.socket_talkto_c.send(tosend.encode('ASCII'))
                 
            time.sleep(1)


    def subscribe_toserverthread(self):
        while(1):
            print("input the server ports you want to subsribe.Eg 1000 1001")
            p1, p2 = input().split(" ")
            p1, p2 = int(p1), int(p2)
            self.Subscribe_Server(p1, p2)

    def Subscribe_Server(self, port1, port2):
         
        self.socket_talkto_parent.connect ("tcp://localhost:%s" % str(port2))
        self.socket_talkto_parent.setsockopt(zmq.SUBSCRIBE, b"")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)

        socket.connect("tcp://localhost:"+str(port1))
        request = dict()
        request['service'] = "GetArticlesforServer"
        request['unique_id'] = self.uniqueid
        request['Type'] = ''
        request['Author'] = ''
        request['Published_after'] = ''
        tosend = json.dumps(request)
        socket.send(tosend.encode('ASCII'))
        # print("going to sleep")
        # time.sleep(20)
        # print("woken up")
        #  Get the reply.
        response = socket.recv()
        response = response.decode('ASCII')
        print("GetArticlesforServer reply "+response)
        response = json.loads(response)
        if(response['status'] == 'FAIL'):
            print(response['status'])
        else:
             
            for i in response['articles']:
                if(i[4] not in  self.articles_id):
                    self.articles_id.add(i[4])
                    day,  month, year = i[2].split("/")
                    c = date(int(year), int(month), int(day))

                    self.articles.append((i[0], i[1], c, i[3], i[4]))

                
    
    def pub_sub(self):
        
        while(1):
            message = self.socket_talkto_parent.recv()
            message = message.decode('ASCII')
            print("Received article from parent server: %s" % message)
            message = json.loads(message)
            self.lock.acquire()            
            if(message['article_id'] not in self.articles_id):                 
                year, month, day = message['date'].split("-")
                c = date(int(year), int(month), int(day))
                print("Appending article received from parent server")
                self.articles_id.add(message['article_id'])
                self.articles.append((message['Type'], message['Author'], c, message['Content'], message['article_id']))
                self.lock.release()
                message = json.dumps(message)
                self.socket_talkto_child.send(message.encode("ASCII"))
            else:
                self.lock.release()
          



