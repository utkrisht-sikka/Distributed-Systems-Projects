import time
import grpc
import pubsub_sys_pb2
import pubsub_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock

class RegistryServer(pubsub_sys_pb2_grpc.RegistryServiceServicer):
    
    def __init__(self, ip="localhost", port=5555, max_servers=5):
        self.address = ip + ":" + str(port)
        self.max_servers = max_servers
        self.servers = {} #"address:name"
        self.lock = Lock()
        
    
    def RegisterServer(self, request, context):
        
        self.lock.acquire()
        
        server_address = request.address
        server_name = request.name
        
        print(f"JOIN REQUEST FROM {server_name}-{server_address}")
        
        if(server_address in list(self.servers.keys())):
            # Here, we assume that if the server is already a part of the registry_server and still sends a register request, then we still return a SUCCESS response as the server has effectively "REGISTERED" at the registry_server
            print("  |-> Server already registered.")
            self.lock.release()
            return pubsub_sys_pb2.RegisterServerResponse(
                status="SUCCESS",
                message="Server already registered with registry."
            )
                
        if(len(self.servers) < self.max_servers):
            try:
                self.servers[server_address] = server_name
                print(f"  |-> Successfully registered\n  |-> Servers List : {self.servers}")
                self.lock.release()
                return pubsub_sys_pb2.RegisterServerResponse(
                    status="SUCCESS",
                    message="Server successfully registered with registry."
                )
            except:
                print(f" |-> Failed to register server")
                self.lock.release()
                return pubsub_sys_pb2.RegisterServerResponse(
                    status="FAIL",
                    message="Failed to register server with registry."
                )
        else:
            print(f" |-> Failed to register server, max server count reached")
            self.lock.release()
            return pubsub_sys_pb2.RegisterServerResponse(
                status="FAIL",
                message="Failed to register server with registry. Max server count reached."
            )
    
    def GetServerList(self, request, context):
        self.lock.acquire()
        # time.sleep(15)
        print(f"SERVER LIST REQUEST FROM : {request.client.name}-{request.client.unique_id}")
        server_list_response = pubsub_sys_pb2.GetServerListResponse()
        for server_address,server_name in self.servers.items():
            server_item = server_list_response.server_list.add()
            server_item.name = server_name
            server_item.address = server_address
        self.lock.release()
        return server_list_response
            
            

if __name__ == "__main__":
    registry_server_object = RegistryServer(ip="localhost", port=5555, max_servers=5)
    grpc_registry_server = grpc.server(futures.ThreadPoolExecutor())
    pubsub_sys_pb2_grpc.add_RegistryServiceServicer_to_server(registry_server_object, grpc_registry_server)
    grpc_registry_server.add_insecure_port(registry_server_object.address)
    print(f" ------------ Starting Registry Server at {registry_server_object.address}--------------------")
    grpc_registry_server.start()
    grpc_registry_server.wait_for_termination()


    