import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
import uuid

REGISTRY_ADDRESS = "localhost:5555"

class Client:
    
    def __init__(self):
        self.id = str(uuid.uuid1())

    def get_replica_list(self, stub):
        
        replica_list_request = readwrite_sys_pb2.GetReplicaListRequest()
        replica_list_request.client.client_id = self.id  
        replica_list_response = stub.GetReplicaList(replica_list_request)
        return replica_list_response
    
    def write(self, stub, Name, Content, uuid):
        write_file_request = readwrite_sys_pb2.WriteRequest()
        write_file_request.Name = Name
        write_file_request.Content = Content
        write_file_request.uuid = uuid
        write_file_response = stub.write(write_file_request)
        return write_file_response
    
    def read(self, stub, uuid):
        read_file_request = readwrite_sys_pb2.ReadRequest()
        read_file_request.uuid = uuid
        read_file_response = stub.read(read_file_request)
        return read_file_response


    def delete(self, stub, uuid):
        delete_file_request = readwrite_sys_pb2.DeleteRequest()
        delete_file_request.uuid = uuid
        delete_file_response = stub.delete(delete_file_request)
        return delete_file_response
    
if __name__ == "__main__":
# def main():

    client_object = Client()
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServiceStub(channel)
        
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            for replica_obj in get_replica_list_response.replica_list:
                print(f"-> {replica_obj.address}")


        while True: 
            print("----------- Client Requests -----------")
            print("1 -> Get servers list from registry server\n2 -> Write a File\n3 -> Read a File\n4 -> Delete a File\n")
            print("---------------------------------------\n")
            request_input = input(">> Enter the option number : ")

            if request_input == '1':
                get_replica_list_response = client_object.get_replica_list(registry_stub)
                print("List of replicas received from registry:")
                if(len(get_replica_list_response.replica_list) == 0):
                    print("[Empty list]")
                else:
                    for replica_obj in get_replica_list_response.replica_list:
                        print(f"-> {replica_obj.address}")

            if request_input == '2':
                input_server_address = input("Enter server address : ")
                input_file_name = input("Enter file name : ")
                input_file_content = input("Enter file content : ")
                input_file_uuid = input("Enter file uuid : ")
                # try:
                with grpc.insecure_channel(input_server_address) as channel:
                    server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                    write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
                    print(f"->Status : {write_file_response.Status}")
                    print(f"->uuid : {write_file_response.uuid}")
                    print(f"->Version : {(write_file_response.Version).ToDatetime()}")
                # except:
                #     print("Could not connect to the server. Please check the server address.")
            
            if request_input == '3':
                input_server_address = input("Enter server address : ")
                input_file_uuid = input("Enter file uuid : ")
                # try:
                with grpc.insecure_channel(input_server_address) as channel:
                    server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                    read_file_response = client_object.read(server_stub, input_file_uuid)
                    print(f"->Status : {read_file_response.Status}")
                    print(f"->Name : {read_file_response.Name}")
                    print(f"->Content : {read_file_response.Content}")
                    print(f"->Version : {(read_file_response.Version).ToDatetime()}")
                # except:
                #     print("Could not connect to the server. Please check the server address.")
            
            if request_input == '4':
                input_server_address = input("Enter server address : ")
                input_file_uuid = input("Enter file uuid : ")
                # try:
                with grpc.insecure_channel(input_server_address) as channel:
                    server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                    delete_file_response = client_object.delete(server_stub, input_file_uuid)
                    print(f"->Status : {delete_file_response.Status}")
                # except:
                #     print("Could not connect to the server. Please check the server address.")

            print("\n\n---------------------------------------\n\n")    
        # except:
        #     print("COULD NOT CONNECT TO REGISTRY SERVER. PLEASE TRY AGAIN. [client]")
            
            