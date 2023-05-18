import time
import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
from concurrent import futures
from threading import Thread
import uuid
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp

REGISTRY_ADDRESS = "localhost:5555"

class Client:
    def getServerList(self,stub):
        print("In getServerList method in Client")
        request_input = readwrite_sys_pb2.Empty();
        get_server_list_response = stub.getServerList(request_input);
        # get_server_list_response = get_server_list_response.split("\n")
        resulting_list=[];
        ind = 1;
        for address in get_server_list_response:
            print("{}th server in get_server_list_response is address={}".format(ind,address.message_val));
            ind+=1;
            resulting_list.append(address.message_val);
        return resulting_list;
        
    def getReadServers(self,stub):
        print("In getReadServers method in Client")
        request_input = readwrite_sys_pb2.Empty();
        read_servers_list = stub.getReadServers(request_input);
        resulting_list=[]
        for temp in read_servers_list:
            resulting_list.append(temp.message_val);
        # get_server_list_response = get_server_list_response.split("\n")
        print("reached here in getReadServers")
        return resulting_list;
    
    def getWriteServers(self,stub):
        print("In getWriteServers method in Client")
        request_input = readwrite_sys_pb2.Empty();
        write_servers_list = stub.getWriteServers(request_input);
        resulting_list=[]
        for temp in write_servers_list:
            resulting_list.append(temp.message_val);
        # get_server_list_response = get_server_list_response.split("\n")
        print("reached here in getWriteServers")
        return resulting_list;


    def write(self, stub, name, content, uuid):
        write_file_request = readwrite_sys_pb2.WriteRequest()
        write_file_request.name = name
        write_file_request.content = content
        write_file_request.uuid = uuid
        print("Before write request ",write_file_request)
        write_file_response = stub.write(write_file_request)

        print("After write request")
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
def main():

    N_r,N_w,N = 0,0,0;
    client_object = Client()
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        
        new_get_list = client_object.getServerList(registry_stub);

    N = len(new_get_list);
    while True: 
        print("----------- Client Requests -----------")
        print("1 -> Get servers list from registry server")
        print("2 -> Write a File")
        print("3 -> Read a File")
        print("4 -> Delete a File")
        print("---------------------------------------\n")
        request_input = input(">> Enter the option number : ")
        get_replica_list_response=[]
        
        if request_input == '1':
            with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
                registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
                
                get_replica_list_response = client_object.getServerList(registry_stub)
                print("STARTUP: List of replicas received from registry:")
                if(len(get_replica_list_response) == 0):
                    print("[Empty list]")
                else:
                    for replica_obj in get_replica_list_response:
                        print(f"server_address-> {replica_obj}")
                new_get_list = get_replica_list_response;
                N = len(get_replica_list_response);
        elif request_input == '2':
            input_file_name = input("Enter file name : ")
            input_file_content = input("Enter file content : ")
            input_file_uuid = input("Enter file uuid : ")
            try:
                new_write_server_list=[]
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    write_server_list = client_object.getWriteServers(registry_server_stub);
                    N_w = len(write_server_list);
                    new_write_server_list = write_server_list;
                # new_write_server_list = ["localhost:5556"]
                for temp in new_write_server_list:
                    input_server_address = temp
                    print("server_address={}".format(input_server_address));
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
                        print(f"->status : {write_file_response.status}")
                        print(f"->uuid : {write_file_response.uuid}")
                        time_stamp_protobuf = write_file_response.version;
                        datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                        datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                        new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                        formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                        
                        print(f"->version : {formatted_timestamp}")
                print("-----------     \n\n\n\n\n --------------");
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
                        
                        

                
                
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))
            
    
        elif request_input == '3':
            
            input_file_uuid = input("Enter file uuid : ")
            try:
                new_read_servers_list=[]
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    
                    read_server_list = client_object.getReadServers(registry_server_stub);
                    N_r = len(read_server_list)
                    new_read_servers_list = read_server_list;
                final_updated_read_response = None;
                final_updated_timestamp = -10**18;
                for i in range(N_r):
            
                    input_server_address = new_read_servers_list[i]
                    
                    input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        
                        if(time_stamp_protobuf.seconds>0):
                            if(time_stamp_protobuf.nanos>final_updated_timestamp):
                                final_updated_timestamp = time_stamp_protobuf.nanos;
                                final_updated_read_response = read_file_response

                            # set_two.add(input_server_address);
                        elif(time_stamp_protobuf.seconds<0):
                            formatted_timestamp = "0001-01-01 00:00:00"

                print("Most recent response of read operation is : ")
                print(f"->Status : {final_updated_read_response.status}")
                print(f"->Name : {final_updated_read_response.name}")
                print(f"->Content : {final_updated_read_response.content}")
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S")
                print(f"->version : {formatted_timestamp}") 

                print("\n\n\n\n -------       \n\n\n\n\n")
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
                
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))

        elif request_input == '4':
            input_file_uuid = input("Enter file uuid : ")
            # try:
            new_delete_server_list=[]
            try:
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    delete_server_list = client_object.getWriteServers(registry_server_stub);
                    N_w = len(delete_server_list);
                    new_delete_server_list = delete_server_list;
                for temp in new_delete_server_list:
                    input_server_address = temp
                    print("server_address={}".format(input_server_address));
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        delete_file_response = client_object.delete(server_stub, input_file_uuid)
                        print(f"->status : {delete_file_response.status}")
                print("-----------   \n\n\n\n\n\n")
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))
        else:
            print("You have pressed an incorrect option please try again");

        print("\n\n---------------------------------------\n\n")  
      
        
    # except:
    #     print("COULD NOT CONNECT TO REGISTRY SERVER. PLEASE TRY AGAIN. [client]")
    
if __name__ == "__main__":
    N_r,N_w,N = 0,0,0;
    client_object = Client()
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        
        new_get_list = client_object.getServerList(registry_stub);

    N = len(new_get_list);
    while True: 
        print("----------- Client Requests -----------")
        print("1 -> Get servers list from registry server")
        print("2 -> Write a File")
        print("3 -> Read a File")
        print("4 -> Delete a File")
        print("---------------------------------------\n")
        request_input = input(">> Enter the option number : ")
        get_replica_list_response=[]
        
        if request_input == '1':
            with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
                registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
                
                get_replica_list_response = client_object.getServerList(registry_stub)
                print("STARTUP: List of replicas received from registry:")
                if(len(get_replica_list_response) == 0):
                    print("[Empty list]")
                else:
                    for replica_obj in get_replica_list_response:
                        print(f"server_address-> {replica_obj}")
                new_get_list = get_replica_list_response;
                N = len(get_replica_list_response);
        elif request_input == '2':
            input_file_name = input("Enter file name : ")
            input_file_content = input("Enter file content : ")
            input_file_uuid = input("Enter file uuid : ")
            try:
                new_write_server_list=[]
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    write_server_list = client_object.getWriteServers(registry_server_stub);
                    N_w = len(write_server_list);
                    new_write_server_list = write_server_list;
                # new_write_server_list = ["localhost:5556"]
                for temp in new_write_server_list:
                    input_server_address = temp
                    print("server_address={}".format(input_server_address));
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
                        print(f"->status : {write_file_response.status}")
                        print(f"->uuid : {write_file_response.uuid}")
                        time_stamp_protobuf = write_file_response.version;
                        datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                        datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                        new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                        formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                        
                        print(f"->version : {formatted_timestamp}")
                print("-----------     \n\n\n\n\n --------------");
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
                        
                        

                
                
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))
            
    
        elif request_input == '3':
            
            input_file_uuid = input("Enter file uuid : ")
            try:
                new_read_servers_list=[]
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    
                    read_server_list = client_object.getReadServers(registry_server_stub);
                    N_r = len(read_server_list)
                    new_read_servers_list = read_server_list;
                final_updated_read_response = None;
                final_updated_timestamp = -10**18;
                for i in range(N_r):
            
                    input_server_address = new_read_servers_list[i]
                    
                    input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        
                        if(time_stamp_protobuf.seconds>0):
                            if(time_stamp_protobuf.nanos>final_updated_timestamp):
                                final_updated_timestamp = time_stamp_protobuf.nanos;
                                final_updated_read_response = read_file_response

                            # set_two.add(input_server_address);
                        elif(time_stamp_protobuf.seconds<0):
                            formatted_timestamp = "0001-01-01 00:00:00"

                print("Most recent response of read operation is : ")
                print(f"->Status : {final_updated_read_response.status}")
                print(f"->Name : {final_updated_read_response.name}")
                print(f"->Content : {final_updated_read_response.content}")
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S")
                print(f"->version : {formatted_timestamp}") 

                print("\n\n\n\n -------       \n\n\n\n\n")
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
                
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))

        elif request_input == '4':
            input_file_uuid = input("Enter file uuid : ")
            # try:
            new_delete_server_list=[]
            try:
                with grpc.insecure_channel(REGISTRY_ADDRESS) as main_channel:
                    registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(main_channel);
                    delete_server_list = client_object.getWriteServers(registry_server_stub);
                    N_w = len(delete_server_list);
                    new_delete_server_list = delete_server_list;
                for temp in new_delete_server_list:
                    input_server_address = temp
                    print("server_address={}".format(input_server_address));
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        delete_file_response = client_object.delete(server_stub, input_file_uuid)
                        print(f"->status : {delete_file_response.status}")
                print("-----------   \n\n\n\n\n\n")
                for i in range(N):
                    print("server here={}".format(new_get_list[i]))
            
                    input_server_address = new_get_list[i]
                    
                    # input_file_uuid = input_file_uuid
                    # try:
                    with grpc.insecure_channel(input_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        read_file_response = client_object.read(server_stub, input_file_uuid)
                        time_stamp_protobuf = read_file_response.version;
                        print(f"->Status : {read_file_response.status}")
                        print(f"->Name : {read_file_response.name}")
                        print(f"->Content : {read_file_response.content}")
            except Exception as arg:
                print("Could not connect to the server. Please check the server address. exp={}".format(arg))
        else:
            print("You have pressed an incorrect option please try again");

        print("\n\n---------------------------------------\n\n")  
      
        
    # except:
    #     print("COULD NOT CONNECT TO REGISTRY SERVER. PLEASE TRY AGAIN. [client]")
            
            