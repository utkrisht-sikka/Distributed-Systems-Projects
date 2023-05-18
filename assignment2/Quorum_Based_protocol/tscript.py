from datetime import datetime, timezone
import Registry_Server
import Server
import Client
import time
import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
import uuid
from concurrent import futures
from threading import Thread
from google.protobuf.timestamp_pb2 import Timestamp

from multiprocessing import Process
def test1():
    print("--------------------------------------------------a------------------------------------------------------")
    N = 4
    N_r,N_w = 2,3;
    rs = Process(target = Registry_Server.main, args=(N_r,N_w,N,0,));
    rs.start()
    time.sleep(1)

    print("--------------------------------------------------b------------------------------------------------------")
    # N = 5
 
    s = []
    for i in range(N):
        s.append(Process(target = Server.main, args=("localhost", str(5556+i),  "SERVER_"+str(i), 0,)))
        
    for i in s:
        i.start()
        time.sleep(2)
    
    print("--------------------------------------------------c------------------------------------------------------")
    for i in s:
        i.join()

    rs.join()
    
    
def test2():
    N = 4
    N_r,N_w = 2,3;
    rs = Process(target = Registry_Server.main, args=(N_r,N_w,N,50,));
    rs.start()
    time.sleep(1)

    

    s = []
    for i in range(N):
        # s.append(Process(target = Server.main, args=("localhost", str(5556+i),  r"C:\Ddrive\classroom\sem8\DSCD\assignment2\Primary_backup_protocol_blocking\s"+str(i), 45,)))
        s.append(Process(target = Server.main, args=("localhost", str(5556+i),"SERVER_"+str(i), 45,)))
    for i in s:
        i.start()
        time.sleep(2)

    
    
    client_object = Client.Client()
    with grpc.insecure_channel(Client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        get_replica_list_response = client_object.getServerList(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response) == 0):
            print("[Empty list]")
        else:
            valid = ["localhost:5556","localhost:5557","localhost:5558","localhost:5559"]
            for i in range(len(valid)):
                print(f"-> {get_replica_list_response[i]}")
                assert valid[i] ==  get_replica_list_response[i]

    print("---------------------------")
    print("\n\n\n\n\n\n")
    print("Printing 1st operation");
    f1 = str(uuid.uuid4())
    get_write_server_list=[]
    with grpc.insecure_channel(Client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        get_write_server_list = client_object.getWriteServers(registry_stub)
    assert(N_w == len(get_write_server_list));
    set_one=set()
    for i in range(N_w):        
        input_server_address = get_write_server_list[i]
        input_file_name = "marks.txt"
        input_file_content = "hi hello"
        input_file_uuid = f1
        # try:
        
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
            print(f"->Status : {response.status}")
            print(f"->uuid : {response.uuid}")
            time_stamp_protobuf = response.version;
            
            if(time_stamp_protobuf.seconds>0):
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                
                print(f"->version : {formatted_timestamp}")
                set_one.add(input_server_address);
            elif(time_stamp_protobuf.seconds<0):
                formatted_timestamp = "0001-01-01 00:00:00"
                print(f"->version : {formatted_timestamp}")
            assert "SUCCESS" ==  response.status     
            assert response.uuid ==  f1;
    print("---------------------------")
    print("\n\n\n\n\n\n")
    print(" -- Printing state of each replica after this operation");
    print(" -- State of each replica after operation 1 -- ")
    set_two=set()
    for i in range(N):
            
        input_server_address = get_replica_list_response[i]
        
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.status}")
            print(f"->Name : {read_file_response.name}")
            print(f"->Content : {read_file_response.content}")
            time_stamp_protobuf = read_file_response.version;
            
            if(time_stamp_protobuf.seconds>0):
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                
                print(f"->version : {formatted_timestamp}")
                set_two.add(input_server_address);
            elif(time_stamp_protobuf.seconds<0):
                formatted_timestamp = "0001-01-01 00:00:00"
                print(f"->version : {formatted_timestamp}")
    assert(set_one.intersection(set_two)==set_one);
    print("---------------------------")
    print("\n\n\n\n\n\n")

    ### --- write on another file
    print("Printing 1st(b) operation -> write on another file");
    f2 = str(uuid.uuid4())
    get_write_server_list=[]
    with grpc.insecure_channel(Client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        get_write_server_list = client_object.getWriteServers(registry_stub)
    assert(N_w == len(get_write_server_list));
    set_one=set()
    for i in range(N_w):        
        input_server_address = get_write_server_list[i]
        input_file_name = "marks2.txt"
        input_file_content = "hi hello bye"
        input_file_uuid = f2
        # try:
        
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
            print(f"->Status : {response.status}")
            print(f"->uuid : {response.uuid}")
            time_stamp_protobuf = response.version;
            
            if(time_stamp_protobuf.seconds>0):
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                
                print(f"->version : {formatted_timestamp}")
                set_one.add(input_server_address);
            elif(time_stamp_protobuf.seconds<0):
                formatted_timestamp = "0001-01-01 00:00:00"
                print(f"->version : {formatted_timestamp}")
            assert "SUCCESS" ==  response.status     
            assert response.uuid ==  f2;
    print(" -- Printing state of each replica after this operation");
    print("---------------------------")
    print("\n\n\n\n\n\n")
    print(" -- State of each replica after operation 1(b) write -- ")
    set_two=set()
    for i in range(N):
            
        input_server_address = get_replica_list_response[i]
        
        input_file_uuid = f2
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.status}")
            print(f"->Name : {read_file_response.name}")
            print(f"->Content : {read_file_response.content}")
            time_stamp_protobuf = read_file_response.version;
            
            if(time_stamp_protobuf.seconds>0):
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                
                print(f"->version : {formatted_timestamp}")
                set_two.add(input_server_address);
            elif(time_stamp_protobuf.seconds<0):
                formatted_timestamp = "0001-01-01 00:00:00"
                print(f"->version : {formatted_timestamp}")
    assert(set_one.intersection(set_two)==set_one);

    print("---------------------------")
    print("\n\n\n\n\n\n")
    get_write_server_list=[]
    with grpc.insecure_channel(Client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
        get_write_server_list = client_object.getWriteServers(registry_stub)
    assert(N_w == len(get_write_server_list));
    set_three = set();
    for i in range(N_w):
            
        input_server_address = get_write_server_list[i]
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.delete(server_stub, input_file_uuid)
            print(f"->Status : {response.status}")
            if("SUCCESS".find(response.status)!=-1):
                set_three.add(input_server_address);
            # assert "FILE DOES NOT EXIST" ==  response.status
    assert(len(set_one.intersection(set_three))>=1);
    print("---------------------------")
    print("\n\n\n\n\n\n")
    print(" -- State of each replica after operation 2 delete -- ")
    updated_count_for_delete = 0;
    for i in range(N):
            
        input_server_address = get_replica_list_response[i]
        
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.status}")
            print(f"->Name : {read_file_response.name}")
            print(f"->Content : {read_file_response.content}")
            if(read_file_response.status.find("FILE DOES NOT EXIST")!=-1 or read_file_response.status.find("FILE ALREADY DELETED")!=-1):
                updated_count_for_delete+=1;

            time_stamp_protobuf = read_file_response.version;
            
            if(time_stamp_protobuf.seconds>0):
                datetime_obj = datetime.fromtimestamp(time_stamp_protobuf.seconds, timezone.utc)
                datetime_obj = datetime_obj.replace(microsecond=time_stamp_protobuf.nanos // 1000)
                new_timestamp = datetime_obj.strftime("%d/%m/%Y %H:%M:%S") 

                formatted_timestamp = datetime.strptime(new_timestamp, "%d/%m/%Y %H:%M:%S") 
                
                print(f"->version : {formatted_timestamp}")
            elif(time_stamp_protobuf.seconds<0):
                formatted_timestamp = "0001-01-01 00:00:00"
                print(f"->version : {formatted_timestamp}")
    assert(updated_count_for_delete>=N_w);

    print("--------------------------- 2nd operation finished --------------")
    print("\n\n\n\n\n\n")
    for i in s:
        i.join()

    rs.join()    

if __name__ == '__main__':
    # test1()
    test2()
    