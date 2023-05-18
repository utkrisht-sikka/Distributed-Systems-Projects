from Server import Server
from threading import Thread
import time
import uuid
unique_id = str(uuid.uuid1())
obj = Server(5556, 5557, unique_id, "Spotify")
# time.sleep(5)
thread = Thread(target = obj.pub_sub)
thread.start()
thread = Thread(target = obj.subscribe_toserverthread)
thread.start()

# time.sleep(10)
# obj.Subscribe_Server(5558, 5559)
obj.Run()
