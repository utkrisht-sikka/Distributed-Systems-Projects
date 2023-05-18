import grpc
import map_reduce_sys_pb2
import map_reduce_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import os
import shutil
import time

MASTER_ADDRESS = "localhost:5555"
DATA_DIR = os.path.join(os.getcwd(), "workers_data_dir")

class Mapper:

    def  __init__(self, ip, port, dir_path, verbose=False):
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        self.verbose = verbose
        self.worker_directory = os.path.join(DATA_DIR, dir_path)
        
        if not os.path.isdir(self.worker_directory):
            os.makedirs(self.worker_directory)
            
    def register_worker(self, stub):
        registration_request = map_reduce_sys_pb2.RegisterWorkerRequest(address=self.address, worker_type="mapper")
        registration_response = stub.RegisterWorker(registration_request)
        return registration_response

    def MapTaskAssignment(self, request, context):
        print("-> Worker assigned map task") if self.verbose else None
        assigned_splits = request.assigned_input_splits
        num_reducers = request.R
        print(f"   |-> Assigned splits : {assigned_splits}") if self.verbose else None
        
        print("   |-> Starting map operation in background\n") if self.verbose else None
        perform_map_operation = Thread(target=self.perform_map_operation, args=(assigned_splits, num_reducers))
        perform_map_operation.start()
        
        return map_reduce_sys_pb2.MapTaskAssignmentResponse(
            status="SUCCESS",
            message="Map task assigned successfully"
        )
        
    def map(self, key, value):
        word_count_store = []
        for word in value:
            word_count_store.append((word, 1))
        return word_count_store
    
    def partition_func(self, val, R):
        return (len(val) % R) if ((len(val) % R) != 0) else R
    
    def partition(self, IF_contents, R):
        num_partitions = R
        partition_files = {f"partition_{i}":[] for i in range(1, num_partitions + 1)}
        for word, cnt in IF_contents:
            partition_num = self.partition_func(word, R)
            partition_files[f"partition_{partition_num}"].append((word, cnt))
        print("-> [MAP]: Creating partition files ....") if self.verbose else None
        for i in range(1, num_partitions + 1):
            f = open(os.path.join(self.worker_directory, f'partition_{i}.txt'), 'a')
            for word, cnt in partition_files[f"partition_{i}"]:
                f.write(f"{word} {cnt}\n")
            f.close()
        return partition_files.keys()
    
    def perform_map_operation(self, assigned_splits, num_reducers):
        
        print(f"-> [MAP]: Processing splits") if self.verbose else None
        intermediate_file = open(os.path.join(self.worker_directory, 'IF.txt'), 'a')
        for split in assigned_splits:
            split_file = open(split, 'r')
            file_contents = split_file.read().splitlines()
            split_file.close()
            for idx, line in enumerate(file_contents):
                words = line.split(' ')
                words = [x.lower() for x in words]
                word_cnt_store = self.map(idx, words)
                for word, cnt in word_cnt_store:
                    intermediate_file.write(f"{word} {cnt}\n")
        intermediate_file.close()
        
        print(f"-> [MAP]: Written to IF, Now creating partitions ....") if self.verbose else None       
        IF_contents = self.read_word_cnt_file(os.path.join(self.worker_directory, 'IF.txt'))
        partition_files = self.partition(IF_contents, R=num_reducers)
        partition_file_list = [os.path.join(self.worker_directory, x + '.txt') for x in partition_files]

        print("-> [MAP]: All done.. Now notifying master about map operation completion") if self.verbose else None
        time.sleep(5)
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            master_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            map_worker_notification_request = map_reduce_sys_pb2.MapWorkerNotificationRequest(
                worker_address=self.address,
                task_status="completed",
                partition_files=partition_file_list
            )
            map_worker_notification_response = master_stub.MapWorkerNotification(map_worker_notification_request)
        print("[MAP]: Map operation completed at worker. Master notified of map completion at worker") if self.verbose else None

    
    def read_word_cnt_file(self, filepath):
        f = open(filepath, 'r')
        return [(x.split(' ')[0], x.split(' ')[1]) for x in f.read().splitlines()]      
    
def main(ip, port, dir_name, timeout):
    mapper_obj = Mapper(ip, port, dir_name)

    if(mapper_obj.address == "localhost:5555"):
        print("Address already taken by master")
    
    else:
        print(f"---> DEPLOYING MAPPER {mapper_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = mapper_obj.register_worker(registry_stub)
            print(f"Mapper registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_worker = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_MapperServiceServicer_to_server(mapper_obj, grpc_worker)
                grpc_worker.add_insecure_port(mapper_obj.address)
                print(f"-------- Starting Mapper : {mapper_obj.address} --------\n")
                grpc_worker.start()
                if(timeout != 0):
                    grpc_worker.wait_for_termination(timeout=timeout)
                else:
                    grpc_worker.wait_for_termination()
            else:
                print(f" -------- Failed to start Mapper --------")
        
if __name__ == "__main__":
    
    print("Please enter the details of the worker")
    ip = input("IP : ")
    port = input("Port : ")
    dir_name = input("Directory name: ")
    
    mapper_obj = Mapper(ip, port, dir_name, verbose=True)
    
    if(mapper_obj.address == "localhost:5555"):
        print("Address already taken by master")
    
    else:
        print(f"---> DEPLOYING MAPPER {mapper_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = mapper_obj.register_worker(registry_stub)
            print(f"Mapper registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_worker = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_MapperServiceServicer_to_server(mapper_obj, grpc_worker)
                grpc_worker.add_insecure_port(mapper_obj.address)
                grpc_worker.start()
                print(f"-------- Starting Mapper : {mapper_obj.address} --------\n")
                grpc_worker.wait_for_termination()
            else:
                print(f" -------- Failed to start Mapper --------")
            