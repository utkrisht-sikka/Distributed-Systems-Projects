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

class Reducer:

    def  __init__(self, ip, port, dir_path, verbose=False):
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        self.verbose = verbose
        self.worker_directory = os.path.join(DATA_DIR, dir_path)
        
        if not os.path.isdir(self.worker_directory):
            os.makedirs(self.worker_directory)
            
        
    def register_worker(self, stub):
        registration_request = map_reduce_sys_pb2.RegisterWorkerRequest(address=self.address, worker_type="reducer")
        registration_response = stub.RegisterWorker(registration_request)
        return registration_response
    
    def ReduceTaskAssignment(self, request, context):
        print("-> Worker assigned reduce task") if self.verbose else None
        assigned_partitions = request.assigned_partitions
        reducer_num = request.reducer_num
        output_data_loc = request.output_data_loc
        
        print(f"   |-> Assigned partitions : {assigned_partitions}") if self.verbose else None
        
        print("   |-> Starting reduce operation in background\n") if self.verbose else None
        perform_reduce_operation = Thread(target=self.perform_reduce_operation, args=(reducer_num, assigned_partitions, output_data_loc))
        perform_reduce_operation.start()

        return map_reduce_sys_pb2.ReduceTaskAssignmentResponse(
            status="SUCCESS",
            message="Reduce task assigned successfully"
        )
    
    def perform_reduce_operation(self, reducer_num, assigned_partitions, output_data_loc):
        
        print(f"-> [REDUCE]: Processing partitions") if self.verbose else None
        # time.sleep(5)
        all_partitions_content = []
        for partition in assigned_partitions:
            partition_file = open(partition, 'r')
            file_contents = partition_file.read().splitlines()
            partition_file.close()
            partition_file_contents = [(line.split(" ")[0], int(line.split(" ")[1])) for line in file_contents]
            all_partitions_content.extend(partition_file_contents)
        # print(f"All partitions content = {all_partitions_content}\n")
        
        print("-> [REDUCE]: Performing shuffle and sort.....") if self.verbose else None
        reducer_contents = self.shuffle_and_sort(all_partitions_content)
        # print(f"Reducer contents = {reducer_contents}\n")
        
        # time.sleep(10)
        print(f"-> [REDUCE] Performing reduce()......") if self.verbose else None
        reducer_word_count = {}
        for word in reducer_contents.keys():
            word_key, cnt_value = self.reduce(word, reducer_contents[word])
            reducer_word_count[word_key] = cnt_value
        print(f"-> [REDUCE]: Final Reduce output = {reducer_word_count}\n") if self.verbose else None
        
        # time.sleep(10)
        print("-> [REDUCE]: Writing to output files....") if self.verbose else None
        lines_to_write = []
        for word, cnt in reducer_word_count.items():
            lines_to_write.append(f"{word} {cnt}\n")

        reducer_local_output_file = open(os.path.join(self.worker_directory, f"Output_{reducer_num}.txt"), 'w')
        reducer_local_output_file.writelines(lines_to_write)
        reducer_local_output_file.close()
        
        reducer_final_output_file = open(os.path.join(output_data_loc, f"Output_{reducer_num}.txt"), 'w')
        reducer_final_output_file.writelines(lines_to_write)
        reducer_final_output_file.close()
        
        print("-> [REDUCE]: All done.. Now notifying master about reduce operation completion") if self.verbose else None
        time.sleep(5)
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            master_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            reduce_worker_notification_request = map_reduce_sys_pb2.ReduceWorkerNotificationRequest(
                worker_address=self.address,
                task_status="completed",
                reducer_local_output_loc=os.path.join(self.worker_directory, f"Output_{reducer_num}.txt")
            )
            # print(f"Reduce worker request = {reduce_worker_notification_request}")
            reduce_worker_notification_response = master_stub.ReduceWorkerNotification(reduce_worker_notification_request)
            # print(f"Master notified of Reduce worker completion")
        print("[REDUCE]: Reduce operation completed at worker. Master notified of reduce completion at worker") if self.verbose else None
    
    def shuffle_and_sort(self, all_partitions_content):
        reducer_contents = {}
        for word, cnt in all_partitions_content:
            if word in reducer_contents.keys():
                reducer_contents[word].append(cnt)
            else:
                reducer_contents[word] = [cnt]
        reducer_contents = dict(sorted(reducer_contents.items()))
        return reducer_contents

    def reduce(self, key, value):
        count = 0
        for v in value:
            count += v
        return key, count
    
def main(ip, port, dir_name, timeout):
    reducer_obj = Reducer(ip, port, dir_name)
    if(reducer_obj.address == "localhost:5555"):
        print("Address already taken by master")
    else:
        print(f"---> DEPLOYING REDUCER {reducer_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = reducer_obj.register_worker(registry_stub)
            print(f"REDUCER registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_worker = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_ReducerServiceServicer_to_server(reducer_obj, grpc_worker)
                grpc_worker.add_insecure_port(reducer_obj.address)
                print(f"-------- Starting REDUCER : {reducer_obj.address} --------\n")
                grpc_worker.start()
                if(timeout != 0):
                    grpc_worker.wait_for_termination(timeout=timeout)
                else:
                    grpc_worker.wait_for_termination()
            else:
                print(f" -------- Failed to start REDUCER --------")
    
if __name__ == "__main__":
    
    print("Please enter the details of the reducer")
    ip = input("IP : ")
    port = input("Port : ")
    dir_name = input("Directory name: ")
    
    reducer_obj = Reducer(ip, port, dir_name, verbose=True)
    
    if(reducer_obj.address == "localhost:5555"):
        print("Address already taken by master")
    
    else:
        print(f"---> DEPLOYING REDUCER {reducer_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = reducer_obj.register_worker(registry_stub)
            print(f"REDUCER registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_worker = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_ReducerServiceServicer_to_server(reducer_obj, grpc_worker)
                grpc_worker.add_insecure_port(reducer_obj.address)
                print(f"-------- Starting REDUCER : {reducer_obj.address} --------\n")
                grpc_worker.start()
                grpc_worker.wait_for_termination()
            else:
                print(f" -------- Failed to start REDUCER --------")
            