import grpc
import non_blocking_sys_pb2
import non_blocking_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import uuid

REGISTRY_ADDRESS = "localhost:5555"

class Client:
    
    def get_replica_list(self, stub):
        
        replica_list_request = non_blocking_sys_pb2.GetReplicaListRequest() 
        replica_list_response = stub.GetReplicaList(replica_list_request)
        return replica_list_response
    
    def client_write_replica(self, name, content, uuid, stub):
        client_write_replica_request = non_blocking_sys_pb2.ClientWriteReplicaRequest(
            name=name,
            content=content,
            uuid=uuid
        )
        client_write_replica_response = stub.ClientWriteReplica(client_write_replica_request)
        return client_write_replica_response
    
    def write_operation(self, stub, file_name, file_content, file_uuid):
        write_request = non_blocking_sys_pb2.ClientWriteReplicaRequest(
            name=file_name,
            content=file_content,
            uuid=file_uuid
        )
        write_response = stub.ClientWriteReplica(write_request)
        return write_response
    
    def read_operation(self, stub, file_uuid):
        read_request = non_blocking_sys_pb2.ClientReadReplicaRequest(
            uuid=file_uuid
        )
        read_response = stub.ClientReadReplica(read_request)
        return read_response
    
    def delete_operation(self, stub, file_uuid):
        delete_request = non_blocking_sys_pb2.ClientDeleteReplicaRequest(
            uuid=file_uuid
        )
        delete_response = stub.ClientDeleteReplica(delete_request)
        return delete_response
    
    
def main():
    print("\n------- Starting up the CLIENT -------\n")
    client_object = Client()
    
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        registry_stub = non_blocking_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("CLIENT STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            for replica_obj in get_replica_list_response.replica_list:
                print(f"-> {replica_obj.address}")
                        
        
        while True:
            print("----------- Client Requests -----------")
            print("1 -> Get servers list from registry server\n2 -> Write/update a file\n3 -> Read a file\n4 -> Delete an existing file")
            print("---------------------------------------\n")
            request_input = input(">> Enter the option number : ")
            
            if(request_input == "1"):
                get_replica_list_response = client_object.get_replica_list(registry_stub)
                print("\nList of replicas received from registry:")
                if(len(get_replica_list_response.replica_list) == 0):
                    print("[Empty list]")
                else:
                    for replica_obj in get_replica_list_response.replica_list:
                        print(f"-> {replica_obj.address}")
            if(request_input == "2"):
                replica_address = input("Enter replica address: ")
                print("Enter file details :")
                input_file_name = input("File Name: ")
                input_file_uuid = input("File UUID: ")
                input_file_content = input("File Content: ")
                
                with grpc.insecure_channel(replica_address) as channel:
                    replica_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                    client_write_request = non_blocking_sys_pb2.ClientWriteReplicaRequest(
                        name=input_file_name,
                        uuid=input_file_uuid,
                        content=input_file_content
                    )
                    write_response = replica_stub.ClientWriteReplica(client_write_request)
                    print(f"\nResponse received from replica: ")
                    print(f"STATUS: {write_response.status}")
                    print(f"UUID: {write_response.uuid}")
                    print(f"VERSION: {(write_response.version).ToDatetime()}")
            
            if(request_input == "3"):
                replica_address = input("Enter replica address: ")
                input_file_uuid =  input("File UUID: ")
                
                with grpc.insecure_channel(replica_address) as channel:
                    replica_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                    client_read_request = non_blocking_sys_pb2.ClientReadReplicaRequest(uuid=input_file_uuid)
                    read_response = replica_stub.ClientReadReplica(client_read_request)
                    print("\nResponse received from replica: ")
                    print(f"STATUS: {read_response.status}")
                    print(f"NAME: {read_response.name}")
                    print(f"CONTENT: {read_response.content}")
                    print(f"VERSION: {(read_response.version).ToDatetime()}")
            
            if(request_input == "4"):
                replica_address = input("Enter replica address: ")
                input_file_uuid =  input("File UUID: ")
                
                with grpc.insecure_channel(replica_address) as channel:
                    replica_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                    client_delete_request = non_blocking_sys_pb2.ClientDeleteReplicaRequest(
                        uuid=input_file_uuid
                    )
                    delete_response = replica_stub.ClientDeleteReplica(client_delete_request)
                    print("\nResponse received from replica: ")
                    print(f"STATUS: {delete_response.status}")
                    
if __name__ == "__main__":
    main()