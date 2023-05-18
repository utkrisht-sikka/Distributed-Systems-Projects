import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import os
import shutil

class RegistryServer(readwrite_sys_pb2_grpc.RegistryServiceServicer):
    
    def removePreviousStaleDirectories(self):
        try:
            current_directory = os.path.abspath('./');
            data_directory = "SERVER_";
            file_list = os.listdir(current_directory)
            for file_loc in file_list:
                # print(os.path.isdir(os.path.join(current_directory,file_loc)))
                # print(file_loc)
                # print(file_loc.find(data_directory))
                if(os.path.isdir(os.path.join(current_directory,file_loc))):

                    if(file_loc.find(data_directory)!=-1):
                        print("file_loc={}".format(file_loc));
                        shutil.rmtree(os.path.join(current_directory,file_loc));
            new_file_list = os.listdir(current_directory)
            
        except Exception as arg:
            print("error occured in removing previous directories exception={}".format(arg));
    
    def __init__(self, ip="localhost", port=5555):
        self.address = ip + ":" + str(port)
        self.primary_server_address = None
        self.servers = []
        self.lock = Lock()
        self.removePreviousStaleDirectories()
    
    def notify_primary(self, replica_address):
        with grpc.insecure_channel(self.primary_server_address) as channel:
            primary_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            notify_primary_request = readwrite_sys_pb2.NotifyPrimaryRequest(
                replicaAddress=replica_address
            )
            notify_primary_response = primary_stub.NotifyPrimary(notify_primary_request)
            return notify_primary_response
            
    
    def RegisterServer(self, request, context):
        
        self.lock.acquire()
        
        server_address = request.address
        
        print(f"REGISTER REQUEST FROM SERVER : {server_address}")
        
        if(server_address in self.servers):
            print(" |-> Server already registered.")
            self.lock.release()
            return readwrite_sys_pb2.RegisterServerResponse(
                status="SUCCESS",
                message="Server already registered with registry",
                primaryServerAddress=self.primary_server_address
            )
        else:
            try:
                self.servers.append(server_address)
                if self.primary_server_address is None:
                    self.primary_server_address = server_address
                    print(" |-> Primary server address set to: " + server_address)
                else:
                    notify_primary_response = self.notify_primary(server_address)
                    print(f" |-> NOTIFY PRIMARY : {notify_primary_response.status} ({notify_primary_response.message})")
                self.lock.release()
                return readwrite_sys_pb2.RegisterServerResponse(
                    status="SUCCESS",
                    message="Server successfully registered with registry",
                    primaryServerAddress=self.primary_server_address
                )
            except:
                self.lock.release()
                return readwrite_sys_pb2.RegisterServerResponse(
                    status="FAIL",
                    message="Failed to register server.",
                    primaryServerAddress="<None>"
                )

    def GetReplicaList(self, request, context):
        self.lock.acquire()
        print(f"REPLICA LIST REQUEST FROM :{request.client.client_id}")
        replica_list_response = readwrite_sys_pb2.GetReplicaListResponse()
        for replica_address in self.servers:
            replica_item = replica_list_response.replica_list.add()
            replica_item.address = replica_address
        self.lock.release()
        return replica_list_response


# if __name__ == "__main__":
def main(timeout):
    registry_server_object = RegistryServer(ip="localhost", port=5555)
    grpc_registry_server = grpc.server(futures.ThreadPoolExecutor())
    readwrite_sys_pb2_grpc.add_RegistryServiceServicer_to_server(registry_server_object, grpc_registry_server)
    grpc_registry_server.add_insecure_port(registry_server_object.address)
    print(f" ------------ Starting Registry Server at {registry_server_object.address}--------------------")
    grpc_registry_server.start()
    if(timeout != 0):
        grpc_registry_server.wait_for_termination(timeout)
    else:
        grpc_registry_server.wait_for_termination()
