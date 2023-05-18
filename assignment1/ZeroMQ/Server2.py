from Server import Server
from threading import Thread
import time
import uuid
unique_id = str(uuid.uuid1())

obj = Server(5558, 5559, unique_id, "Anime")
# time.sleep(5)
thread = Thread(target = obj.pub_sub)
thread.start()

thread = Thread(target = obj.subscribe_toserverthread)
thread.start()
# obj.Subscribe_Server(5556, 5557)
# print("going to sleep")
# time.sleep(30)
# print("woken up")
# obj.Subscribe_Server(5562, 5563)

obj.Run()
