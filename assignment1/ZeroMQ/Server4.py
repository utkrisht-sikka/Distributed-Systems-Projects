from Server import Server
from threading import Thread
import time
import uuid
unique_id = str(uuid.uuid1())

obj = Server(5562, 5563, unique_id, "Marvel")
# time.sleep(5)
thread = Thread(target = obj.pub_sub)
thread.start()
 
thread = Thread(target = obj.subscribe_toserverthread)
thread.start()
# time.sleep(10)
# obj.Subscribe_Server(5560, 5561)
obj.Run()
