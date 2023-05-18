import registry_server
import server
import client
import time
import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
import uuid

from multiprocessing import Process

 
def test1():
    print("--------------------------------------------------a------------------------------------------------------")
    rs = Process(target = registry_server.main, args=(50,))
    rs.start()
    time.sleep(1)

    print("--------------------------------------------------b------------------------------------------------------")
    N = 5
 
    s = []
    for i in range(N):
        s.append(Process(target = server.main, args=("localhost", str(5556+i),  r"SERVER_"+str(i), 45,)))
        
    for i in s:
        i.start()
        time.sleep(2)
    
    print("--------------------------------------------------c------------------------------------------------------")
    client_object = client.Client()
    with grpc.insecure_channel(client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            valid = ["localhost:5556","localhost:5557","localhost:5558","localhost:5559","localhost:5560"]
            for i in range(len(valid)):
                print(f"-> {get_replica_list_response.replica_list[i].address}")
                assert valid[i] ==  get_replica_list_response.replica_list[i].address
    
    print("--------------------------------------------------d------------------------------------------------------")
    input_server_address = "localhost:5556"
    input_file_name = "a.txt"
    input_file_content = "apple keeps doctor away"
    f1 = str(uuid.uuid1())
    input_file_uuid = f1

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {write_file_response.Status}")
        print(f"->uuid : {write_file_response.uuid}")
        print(f"->Version : {(write_file_response.Version).ToDatetime()}")
        assert "SUCCESS" ==  write_file_response.Status
        assert f1 ==  write_file_response.uuid

    print("--------------------------------------------------e------------------------------------------------------")
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.Status}")
            print(f"->Name : {read_file_response.Name}")
            print(f"->Content : {read_file_response.Content}")
            print(f"->Version : {(read_file_response.Version).ToDatetime()}")
            assert "SUCCESS" ==  read_file_response.Status
            assert input_file_name ==  read_file_response.Name
            assert input_file_content ==  read_file_response.Content

    print("--------------------------------------------------f------------------------------------------------------")
    input_server_address = "localhost:5557"
    input_file_name = "b.txt"
    input_file_content = "doctor keeps apple with him"
    f2 = str(uuid.uuid1())
    input_file_uuid = f2

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {write_file_response.Status}")
        print(f"->uuid : {write_file_response.uuid}")
        print(f"->Version : {(write_file_response.Version).ToDatetime()}")
        assert "SUCCESS" ==  write_file_response.Status
        assert f2 ==  write_file_response.uuid

    print("--------------------------------------------------g------------------------------------------------------")
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f2
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.Status}")
            print(f"->Name : {read_file_response.Name}")
            print(f"->Content : {read_file_response.Content}")
            print(f"->Version : {(read_file_response.Version).ToDatetime()}")
            assert "SUCCESS" ==  read_file_response.Status
            assert input_file_name ==  read_file_response.Name
            assert input_file_content ==  read_file_response.Content


    print("--------------------------------------------------h------------------------------------------------------")
    input_server_address = "localhost:5558"
    input_file_uuid = f2
    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        delete_file_response = client_object.delete(server_stub, input_file_uuid)
        print(f"->Status : {delete_file_response.Status}")
        assert "SUCCESS" ==  delete_file_response.Status

    print("--------------------------------------------------i------------------------------------------------------")
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f2
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.Status}")
            print(f"->Name : {read_file_response.Name}")
            print(f"->Content : {read_file_response.Content}")
            print(f"->Version : {(read_file_response.Version).ToDatetime()}")
            assert "FILE ALREADY DELETED" ==  read_file_response.Status
            assert "" ==  read_file_response.Name
            assert "None" ==  read_file_response.Content

    for i in s:
        i.join()

    rs.join()
  


def test2():
    rs = Process(target = registry_server.main, args=(110,))
    rs.start()
    time.sleep(1)

    N = 4

    s = []
    for i in range(N):
        s.append(Process(target = server.main, args=("localhost", str(5556+i),   "SERVER_"+str(i), 105,)))

    for i in s:
        i.start()
        time.sleep(2)

    
    
    client_object = client.Client()
    with grpc.insecure_channel(client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            valid = ["localhost:5556","localhost:5557","localhost:5558","localhost:5559"]
            for i in range(len(valid)):
                print(f"-> {get_replica_list_response.replica_list[i].address}")
                assert valid[i] ==  get_replica_list_response.replica_list[i].address

    print("sleeping for 1min")
    print("...zzz...")
    print("...zzz...")
    time.sleep(60)
    #---------------------------write and get FILE WITH THE SAME NAME ALREADY EXISTS----------------------
    f1 = str(uuid.uuid1())
    for i in range(N):        
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_name = "marks.txt"
        input_file_content = "hi hello"
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
            print(f"->Status : {response.Status}")
            print(f"->uuid : {response.uuid}")
            print(f"->Version : {(response.Version).ToDatetime()}")
            assert "FILE WITH THE SAME NAME ALREADY EXISTS" ==  response.Status     
            assert "None" ==  response.uuid
            assert "0001-01-01 00:00:00" == str((response.Version).ToDatetime())
    #---------------------------read and get FILE DOES NOT EXIST----------------------
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {read_file_response.Status}")
            print(f"->Name : {read_file_response.Name}")
            print(f"->Content : {read_file_response.Content}")
            print(f"->Version : {(read_file_response.Version).ToDatetime()}")
            assert "FILE DOES NOT EXIST" ==  read_file_response.Status
            assert "None" ==  read_file_response.Name
            assert "None" ==  read_file_response.Content
            assert "0001-01-01 00:00:00" == str((read_file_response.Version).ToDatetime())


    #---------------------------delete and get FILE DOES NOT EXIST----------------------
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.delete(server_stub, input_file_uuid)
            print(f"->Status : {response.Status}")
            assert "FILE DOES NOT EXIST" ==  response.Status

    #---------------------------write and get SUCCESS----------------------
    
            
    input_server_address = get_replica_list_response.replica_list[2].address
    input_file_name = "marks2.txt"
    input_file_content = "hi hello"
    input_file_uuid = f1
    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {response.Status}")
        print(f"->uuid : {response.uuid}")
        print(f"->Version : {(response.Version).ToDatetime()}")
        assert "SUCCESS" ==  response.Status     
        assert f1 ==  response.uuid
    
    #---------------------------write and get SUCCESS----------------------
    
            
    input_server_address = get_replica_list_response.replica_list[3].address
    input_file_name = "marks2.txt"
    input_file_content = "hi hello, bye"
    input_file_uuid = f1
    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {response.Status}")
        print(f"->uuid : {response.uuid}")
        print(f"->Version : {(response.Version).ToDatetime()}")
        assert "SUCCESS" ==  response.Status     
        assert f1 ==  response.uuid
      
    #---------------------------read and get SUCCESS----------------------
    for i in range(N):
            
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {response.Status}")
            print(f"->Name : {response.Name}")
            print(f"->Content : {response.Content}")
            print(f"->Version : {(response.Version).ToDatetime()}")
            assert "SUCCESS" ==  response.Status
            assert "marks2.txt" ==  response.Name
            assert "hi hello, bye" ==  response.Content

    #---------------------------delete and get SUCCESS----------------------
    input_server_address = get_replica_list_response.replica_list[0].address
    input_file_uuid = f1
    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        response = client_object.delete(server_stub, input_file_uuid)
        print(f"->Status : {response.Status}")
        assert "SUCCESS" ==  response.Status

    #--------------------------- again delete and get FILE ALREADY DELETED----------------------
    for i in range(N):
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.delete(server_stub, input_file_uuid)
            print(f"->Status : {response.Status}")
            assert "FILE ALREADY DELETED" ==  response.Status


    #--------------------------- read and get FILE ALREADY DELETED----------------------
    for i in range(N):
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.read(server_stub, input_file_uuid)
            response = client_object.read(server_stub, input_file_uuid)
            print(f"->Status : {response.Status}")
            print(f"->Name : {response.Name}")
            print(f"->Content : {response.Content}")
            print(f"->Version : {(response.Version).ToDatetime()}")
            assert "FILE ALREADY DELETED" ==  response.Status
            assert "" ==  response.Name
            assert "None" ==  response.Content

    
    #---------------------------write and get DELETED FILE CANNOT BE UPDATED----------------------
    for i in range(N):
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_name = "marks2.txt"
        input_file_content = "wakka wakka"
        input_file_uuid = f1
        # try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
            response = client_object.write(server_stub,input_file_name, input_file_content, input_file_uuid)
            print(f"->Status : {response.Status}")
            print(f"->uuid : {response.uuid}")
            print(f"->Version : {(response.Version).ToDatetime()}")
            assert "DELETED FILE CANNOT BE UPDATED" ==  response.Status     
            assert "None" ==  response.uuid

    for i in s:
        i.join()

    rs.join()


def test3():
    print("--------------------------------------------------a------------------------------------------------------")
    rs = Process(target = registry_server.main, args=(50,))
    rs.start()
    time.sleep(1)

    print("--------------------------------------------------b------------------------------------------------------")
    N = 1
 
    s = []
    for i in range(N):
        s.append(Process(target = server.main, args=("localhost", str(5556+i),  "SERVER_"+str(i), 45,)))
        
    for i in s:
        i.start()
        time.sleep(2)
    
    print("--------------------------------------------------c------------------------------------------------------")
    client_object = client.Client()
    with grpc.insecure_channel(client.REGISTRY_ADDRESS) as channel:
        registry_stub = readwrite_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
    
    print("--------------------------------------------------d------------------------------------------------------")
    input_server_address = "localhost:5556"
    input_file_name = "file1"
    input_file_content = "Content-1"
    f1 = str(uuid.uuid1())
    input_file_uuid = f1

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {write_file_response.Status}")
        print(f"->uuid : {write_file_response.uuid}")
        print(f"->Version : {(write_file_response.Version).ToDatetime()}")
        assert "SUCCESS" ==  write_file_response.Status
        assert f1 ==  write_file_response.uuid

    print("--------------------------------------------------e------------------------------------------------------")
    input_server_address = "localhost:5556"
    input_file_name = "file2"
    input_file_content = "Content-1"
    f2 = str(uuid.uuid1())
    input_file_uuid = f2

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {write_file_response.Status}")
        print(f"->uuid : {write_file_response.uuid}")
        print(f"->Version : {(write_file_response.Version).ToDatetime()}")
        assert "SUCCESS" ==  write_file_response.Status
        assert f2 ==  write_file_response.uuid


    print("--------------------------------------------------f------------------------------------------------------")
    input_server_address = "localhost:5556"
    
    input_file_uuid = f1

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.delete(server_stub,  input_file_uuid)
        print(f"->Status : {write_file_response.Status}")


    print("--------------------------------------------------g------------------------------------------------------")
    input_server_address = "localhost:5556"
    input_file_name = "file1"
    input_file_content = "Content-1"
  
    input_file_uuid = f2

    # try:
    with grpc.insecure_channel(input_server_address) as channel:
        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
        write_file_response = client_object.write(server_stub, input_file_name, input_file_content, input_file_uuid)
        print(f"->Status : {write_file_response.Status}")
        print(f"->uuid : {write_file_response.uuid}")
        print(f"->Version : {(write_file_response.Version).ToDatetime()}")
    
    for i in s:
        i.join()

    rs.join()
 
def test4():
    print("--------------------------------------------------a------------------------------------------------------")
    rs = Process(target = registry_server.main, args=(550,))
    rs.start()
    time.sleep(1)

    print("--------------------------------------------------b------------------------------------------------------")
    N = 2
 
    s = []
    for i in range(N):
        s.append(Process(target = server.main, args=("localhost", str(5556+i),  "SERVER_"+str(i), 455,)))
        
    for i in s:
        i.start()
        time.sleep(2)

    for i in s:
        i.join()

    rs.join()

if __name__ == '__main__':
    test1()
    # test2()
    # test3()
    # test4()
   
    