from Client import Client 
import time
import uuid
unique_id = str(uuid.uuid1())
obj = Client(unique_id)

while(1):
    print("Enter 1 to GetServerList")
    print("Enter 2 to JoinServer")
    print("Enter 3 to LeaveServer")
    print("Enter 4 to GetArticles")
    print("Enter 5 to PublishArticle")
    print("Enter 6 to Exit")
    ch = input()
    if(ch == '1'):
        obj.GetServerList()
    elif(ch == '2'):
        print("Enter port number of server")
        port = int(input())
        obj.JoinServer(port)
    elif(ch == '3'):
        print("Enter port number of server")
        port = int(input())
        obj.LeaveServer(port)
    elif(ch == '4'):
        print("Enter port number of server")
        port = int(input())
        print("Enter type")
        type = input()
        print("Enter author")
        author = input()
        print("Enter date. Example 03/02/2023")
        date = input()
        obj.GetArticles(port, type, author, date)
    elif(ch == '5'):
        print("Enter port number of server")
        port = int(input())
        print("Enter type")
        type = input()
        print("Enter author")
        author = input()
        print("Enter content")
        content = input()
        obj.PublishArticle(port, type, author, content)
    elif(ch == '6'):
        break
    else:
        print("wrong input")


        


# print("sleeping")
# time.sleep(5)
# obj.PublishArticle(5556, "SPORTS", "Jack Dorsey", "Messi has won the FIFA World Cup" )
# obj.PublishArticle(5556, "", "Jack Dorsey", "Messi has won the FIFA World Cup" )
# obj.PublishArticle(5556, "", "", "" )
# obj.PublishArticle(5556, "", "Jack Dorsey", "Messi has not won the FIFA World Cup" )
# obj.GetArticles(5556, "SPORTS", "Jack Dorsey", "03/02/2023")
# obj.GetArticles(5556, "", "Jack Dorsey", "03/02/2023")
# obj.GetArticles(5556, "SPORTS", "", "03/02/2023")
# obj.GetArticles(5556, "SPORTS", "Jack Dorsey", "")
# obj.LeaveServer(5556)