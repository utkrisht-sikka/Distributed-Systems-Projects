import registry_server
import server
import client
import time
import grpc
import non_blocking_sys_pb2
import non_blocking_sys_pb2_grpc
import uuid

from multiprocessing import Process

 
# if __name__ == '__main__':

def test1():
    
    print("\n--------------------------------------------------a------------------------------------------------------")
    rs = Process(target = registry_server.main, args=(50,))
    rs.start()
    time.sleep(5)

    print("\n--------------------------------------------------b------------------------------------------------------")
    N = 5
    s = []
    for i in range(1, N + 1):
        s.append(Process(target = server.main, args=("localhost", str(5000 + i), f"SERVER_{i}", 45,)))
        
    for i in s:
        i.start()
        time.sleep(2)
    
    print("\n\n--------------------------------------------------c------------------------------------------------------\n")
    print(f"TEST: Client startup, list of replicas should be received")
    client_object = client.Client()
    with grpc.insecure_channel(client.REGISTRY_ADDRESS) as channel:
        registry_stub = non_blocking_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            try:
                valid = ["localhost:5001","localhost:5002","localhost:5003","localhost:5004","localhost:5005"]
                for i in range(len(valid)):
                    print(f"-> {get_replica_list_response.replica_list[i].address}")
                    assert valid[i] ==  get_replica_list_response.replica_list[i].address
                print("\n[GetReplicas]: Test case PASSED")
            except AssertionError as e:
                print("\n[GetReplicas]: Test case FAILED")
                return
    time.sleep(2)
    print("\n\n--------------------------------------------------d------------------------------------------------------\n")
    input_server_address_1 = "localhost:5002"
    input_file_name_1 = "file1.txt"
    input_file_content_1 = "contents of file-1"
    file1_uuid = str(uuid.uuid1())
    input_file_uuid_1 = file1_uuid
    
    print(f"TEST: Writing file [{file1_uuid}]:{input_file_name_1} with contents: {input_file_content_1}. Write request sent to {input_server_address_1}\n")

    try:
        with grpc.insecure_channel(input_server_address_1) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            write_file_response = client_object.write_operation(server_stub, input_file_name_1, input_file_content_1, input_file_uuid_1)
            print(f"-> Status: {write_file_response.status}")
            print(f"-> UUID: {write_file_response.uuid}")
            print(f"-> Version: {(write_file_response.version).ToDatetime()}")
            assert write_file_response.status == "SUCCESS"
            assert file1_uuid == write_file_response.uuid
            print("---> [Write Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Write Request]: Test case FAILED\n")
        return

    time.sleep(5)
    print("\n\n--------------------------------------------------e------------------------------------------------------\n")
    
    for i in range(N):    
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = file1_uuid
        print(f"TEST: Reading file [{file1_uuid}]. Read request sent to {input_server_address}\n")
        try:
            with grpc.insecure_channel(input_server_address) as channel:
                server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                read_file_response = client_object.read_operation(server_stub, input_file_uuid)
                print(f"-> Status : {read_file_response.status}")
                print(f"-> Name : {read_file_response.name}")
                print(f"-> Content : {read_file_response.content}")
                print(f"-> Version : {(read_file_response.version).ToDatetime()}")
                assert read_file_response.status == "SUCCESS"
                assert read_file_response.name == input_file_name_1
                assert read_file_response.content == input_file_content_1
            print(f"---> [Read Request]: Test case PASSED for replica-{i + 1}\n")
        except AssertionError as e:
            print("[Read Request]: Test case FAILED\n")
            return
    print("\n[Read Request]: Tests PASSED for all replicas")

    print("\n\n--------------------------------------------------f------------------------------------------------------\n")
    input_server_address_2 = "localhost:5003"
    input_file_name_2 = "file2.txt"
    input_file_content_2 = "contents of file2"
    file2_uuid = str(uuid.uuid1())
    input_file_uuid_2 = file2_uuid
    
    print(f"TEST: Writing file [{file2_uuid}]:{input_file_name_2} with contents: {input_file_content_2}. Write request sent to {input_server_address_2}\n")

    try:
        with grpc.insecure_channel(input_server_address_2) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            write_file_response = client_object.write_operation(server_stub, input_file_name_2, input_file_content_2, input_file_uuid_2)
            print(f"-> Status: {write_file_response.status}")
            print(f"-> UUID: {write_file_response.uuid}")
            print(f"-> Version: {(write_file_response.version).ToDatetime()}")
            assert write_file_response.status == "SUCCESS"
            assert file2_uuid == write_file_response.uuid
        print("---> [Write Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Write Request]: Test case FAILED\n")
        return
    time.sleep(5)
    
    print("\n\n--------------------------------------------------g------------------------------------------------------\n")
    
    for i in range(N):      
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = file2_uuid
        print(f"TEST: Reading file [{file2_uuid}]. Read request sent to {input_server_address}")
        try:
            with grpc.insecure_channel(input_server_address) as channel:
                server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                read_file_response = client_object.read_operation(server_stub, input_file_uuid)
                print(f"-> Status : {read_file_response.status}")
                print(f"-> Name : {read_file_response.name}")
                print(f"-> Content : {read_file_response.content}")
                print(f"-> Version : {(read_file_response.version).ToDatetime()}")
                assert read_file_response.status == "SUCCESS"
                assert read_file_response.name == input_file_name_2
                assert read_file_response.content == input_file_content_2
                print(f"---> [Read Request]: Test case PASSED for replica-{i + 1}\n")
        except AssertionError as e:
            print("---> [Read Request]: Test case FAILED\n")
            return
    print("\n[Read Request]: Tests PASSED for all replicas")
    time.sleep(5)

    print("\n\n--------------------------------------------------h------------------------------------------------------\n")
    input_server_address_3 = "localhost:5004"
    input_file_uuid_3 = file2_uuid
    print(f"TEST: Deleting file with uuid={input_file_uuid_3}. Delete request sent to {input_server_address_3}")
    try:
        with grpc.insecure_channel(input_server_address_3) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            delete_file_response = client_object.delete_operation(server_stub, input_file_uuid_3)
            print(f"-> Status : {delete_file_response.status}")
            assert delete_file_response.status == "SUCCESS"
        print("\n[Delete Request]: Test case PASSED")
    except AssertionError as e:
        print("\n[Delete Request]: Test case FAILED")
        return
    time.sleep(5)
    
    print("\n\n--------------------------------------------------i------------------------------------------------------\n")
    for i in range(N):
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = file2_uuid
        
        print(f"TEST: Reading file [{file2_uuid}]. Read request sent to {input_server_address}")
        
        try:
            with grpc.insecure_channel(input_server_address) as channel:
                server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                read_file_response = client_object.read_operation(server_stub, input_file_uuid)
                print(f"-> Status : {read_file_response.status}")
                print(f"-> Name : {read_file_response.name}")
                print(f"-> Content : {read_file_response.content}")
                print(f"-> Version : {(read_file_response.version).ToDatetime()}")
                assert read_file_response.status == "[FAIL]: FILE ALREADY DELETED"
                assert read_file_response.name == ""
                assert read_file_response.content == "<NONE>"
            print(f"---> [Read Request]: Test case PASSED for replica-{i + 1}\n")
        except AssertionError as e:
            print("[Read Request]: Test case FAILED\n")
            return
        
    print("\n[Read Request]: Tests PASSED for all replicas")   
    time.sleep(2)
    
    
    for i in s:
        i.join()

    rs.join()
    
    print("\n\n------------ All test cases PASSED ------------")

def test2():
    print("\n-----------------------------------------(1) Starting Registry------------------------------------------------------")
    rs = Process(target = registry_server.main, args=(50,))
    rs.start()
    time.sleep(5)

    print("\n-----------------------------------------(2) Starting 3 server -----------------------------------------------------\n")
    N = 4
    s = []
    for i in range(1, N + 1):
        s.append(Process(target = server.main, args=("localhost", str(5000 + i), f"SERVER_{i}", 45,)))
        
    for i in s:
        i.start()
        time.sleep(2)
    
    print("\n\n----------------------------------------(3) Client start up ----------------------------------------------------\n")
    print(f"TEST: Client startup, list of replicas should be received")
    client_object = client.Client()
    with grpc.insecure_channel(client.REGISTRY_ADDRESS) as channel:
        registry_stub = non_blocking_sys_pb2_grpc.RegistryServiceStub(channel)
        get_replica_list_response = client_object.get_replica_list(registry_stub)
        print("STARTUP: List of replicas received from registry:")
        if(len(get_replica_list_response.replica_list) == 0):
            print("[Empty list]")
        else:
            try:
                valid = ["localhost:5001","localhost:5002","localhost:5003", "localhost:5004"]
                for i in range(len(valid)):
                    print(f"-> {get_replica_list_response.replica_list[i].address}")
                    assert valid[i] ==  get_replica_list_response.replica_list[i].address
                print("\n[GetReplicas]: Test case PASSED")
            except AssertionError as e:
                print("\n[GetReplicas]: Test case FAILED")
                return
    time.sleep(2)
    print("\n\n---------------------------  (4) Reading non existent file ------------------------------------------------------\n")
    uuid_1 = str(uuid.uuid1())
    input_server_address = "localhost:5002"
    print(f"TEST: Client reads file with uuid = {uuid_1} from {input_server_address}")
    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            read_file_response = client_object.read_operation(server_stub, uuid_1)
            print(f"-> Status : {read_file_response.status}")
            print(f"-> Name : {read_file_response.name}")
            print(f"-> Content : {read_file_response.content}")
            print(f"-> Version : {(read_file_response.version).ToDatetime()}")
            assert read_file_response.status == "[FAIL]: FILE DOES NOT EXIST"
            assert read_file_response.name == "<NONE>"
            assert read_file_response.content == "<NONE>"
            print(f"---> [Read Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Read Request]: Test case FAILED\n")
        return
    time.sleep(2)
    print("\n\n---------------------------  (5) Deleting non existent file -----------------------------------------------------\n")
    input_server_address = "localhost:5003"
    input_file_uuid = uuid_1
    print(f"TEST: Deleting file with uuid={input_file_uuid}. Delete request sent to {input_server_address}")
    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            delete_file_response = client_object.delete_operation(server_stub, input_file_uuid)
            print(f"-> Status : {delete_file_response.status}")
            assert delete_file_response.status == "[FAIL]: FILE DOES NOT EXIST"
        print("\n[Delete Request]: Test case PASSED")
    except AssertionError as e:
        print("\n[Delete Request]: Test case FAILED")
        return
    time.sleep(2)
    print("\n\n---------------------------  (6) Writing file -----------------------------------------------------------------\n")
    file1_uuid = uuid_1
    file1_name = "file1.txt"
    file1_contents = "[test-2]: contents of file-1"
    input_server_address = "localhost:5004"
    input_file_name = file1_name
    input_file_content = file1_contents
    input_file_uuid = file1_uuid
    
    print(f"TEST: Writing file [{file1_uuid}]:{input_file_name} with contents: {input_file_content}. Write request sent to {input_server_address}\n")

    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            write_file_response = client_object.write_operation(server_stub, input_file_name, input_file_content, input_file_uuid)
            print(f"-> Status: {write_file_response.status}")
            print(f"-> UUID: {write_file_response.uuid}")
            print(f"-> Version: {(write_file_response.version).ToDatetime()}")
            assert write_file_response.status == "SUCCESS"
            assert file1_uuid == write_file_response.uuid
            print("---> [Write Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Write Request]: Test case FAILED\n")
        return
    time.sleep(5)
    print("\n\n---------------------------  (7) Reading the written file -----------------------------------------------------\n")
    for i in range(N):
        input_server_address = get_replica_list_response.replica_list[i].address
        input_file_uuid = file1_uuid
        
        print(f"TEST: Reading file [{input_file_uuid}]. Read request sent to {input_server_address}")
        
        try:
            with grpc.insecure_channel(input_server_address) as channel:
                server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                read_file_response = client_object.read_operation(server_stub, input_file_uuid)
                print(f"-> Status : {read_file_response.status}")
                print(f"-> Name : {read_file_response.name}")
                print(f"-> Content : {read_file_response.content}")
                print(f"-> Version : {(read_file_response.version).ToDatetime()}")
                assert read_file_response.status == "SUCCESS"
                assert read_file_response.name == file1_name
                assert read_file_response.content == file1_contents
            print(f"---> [Read Request]: Test case PASSED for replica-{i + 1}\n")
        except AssertionError as e:
            print("[Read Request]: Test case FAILED\n")
            return
    print("\n[Read Request]: Tests PASSED for all replicas")    
    time.sleep(2)
    print("\n\n---------------------------  (8) Write file with same name -----------------------------------------------------\n")
    uuid_2 = str(uuid.uuid1())
    input_server_address = "localhost:5003"
    input_file_name = file1_name
    input_file_content = "[test-2]: contents-2"
    input_file_uuid = uuid_2
    
    print(f"TEST: Writing file [{input_file_uuid}]:{input_file_name} with contents: {input_file_content}. Write request sent to {input_server_address}\n")

    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            write_file_response = client_object.write_operation(server_stub, input_file_name, input_file_content, input_file_uuid)
            print(f"-> Status: {write_file_response.status}")
            print(f"-> UUID: {write_file_response.uuid}")
            print(f"-> Version: {(write_file_response.version).ToDatetime()}")
            assert write_file_response.status == "[FAIL]: FILE WITH THE SAME NAME ALREADY EXISTS"
            assert write_file_response.uuid == "<NONE>"
            print("---> [Write Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Write Request]: Test case FAILED\n")
        return
    time.sleep(3)
    print("\n\n---------------------------  (9) Delete file-1 --------------------------------------------------------------\n")
    input_server_address = "localhost:5004"
    input_file_uuid = file1_uuid
    print(f"TEST: Deleting file with uuid={input_file_uuid}. Delete request sent to {input_server_address}")
    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            delete_file_response = client_object.delete_operation(server_stub, input_file_uuid)
            print(f"-> Status : {delete_file_response.status}")
            assert delete_file_response.status == "SUCCESS"
        print("\n[Delete Request]: Test case PASSED")
    except AssertionError as e:
        print("\n[Delete Request]: Test case FAILED")
        return
    time.sleep(7)
    print("\n\n---------------------------  (9) Write to a deleted file ---------------------------------------------------\n")
    input_server_address = "localhost:5002"
    input_file_name = file1_name
    input_file_content = "[test-2]: updated contents-1"
    input_file_uuid = file1_uuid
    
    print(f"TEST: Writing file [{input_file_uuid}]:{input_file_name} with contents: {input_file_content}. Write request sent to {input_server_address}\n")

    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            write_file_response = client_object.write_operation(server_stub, input_file_name, input_file_content, input_file_uuid)
            print(f"-> Status: {write_file_response.status}")
            print(f"-> UUID: {write_file_response.uuid}")
            print(f"-> Version: {(write_file_response.version).ToDatetime()}")
            assert write_file_response.status == "[FAIL]: DELETED FILE CANNOT BE UPDATED"
            assert write_file_response.uuid == "<NONE>"
            assert str((write_file_response.version).ToDatetime()) == "0001-01-01 00:00:00"
            print("---> [Write Request]: Test case PASSED\n")
    except AssertionError as e:
        print("---> [Write Request]: Test case FAILED\n")
        return
    time.sleep(3)
    print("\n\n---------------------------  (10) Deleting an already deleted file ---------------------------------------\n")
    input_server_address = "localhost:5003"
    input_file_uuid = file1_uuid
    print(f"TEST: Deleting file with uuid={input_file_uuid}. Delete request sent to {input_server_address}")
    try:
        with grpc.insecure_channel(input_server_address) as channel:
            server_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
            delete_file_response = client_object.delete_operation(server_stub, input_file_uuid)
            print(f"-> Status : {delete_file_response.status}")
            assert delete_file_response.status == "[FAIL]: FILE ALREADY DELETED"
        print("\n[Delete Request]: Test case PASSED")
    except AssertionError as e:
        print("\n[Delete Request]: Test case FAILED")
        return
    time.sleep(5)
    
    
    for i in s:
        i.join()

    rs.join()
    
    print("\n\n--------------------------------------- All test cases PASSED -------------------------------------------")
    
    
if __name__ == "__main__":
    # test1()
    test2()