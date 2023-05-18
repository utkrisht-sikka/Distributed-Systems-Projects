from multiprocessing import Process
import grpc
import map_reduce_sys_pb2
import map_reduce_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import os
import shutil
import random
import time
import mapper
import reducer

DATA_DIR = os.path.join(os.getcwd(), "workers_data_dir")

class Master:
    def __init__(self, config_loc, input_data_loc, output_data_loc, ip="localhost", port=5555):
        '''
        config is path to config.txt
        ip_port: ip and port to which master is bound
        '''
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        with open(config_loc, "r") as f:
            lines = f.read().splitlines()
            self.M = int(lines[0][-1])
            self.R = int(lines[1][-1])
        self.lock = Lock()
        self.input_data_loc = input_data_loc
        self.output_data_loc = output_data_loc
        self.workers = {"mapper": {}, "reducer":{}}
        self.task_status = {"map": {}, "reduce": {}}
        if(os.path.isdir(DATA_DIR)):
            dir_contents = os.listdir(DATA_DIR)
            for obj in dir_contents:
                if(os.path.isdir(os.path.join(DATA_DIR, obj)) and (("MAPPER_" in obj) or ("REDUCER_" in obj))):
                    shutil.rmtree(os.path.join(DATA_DIR, obj))
        else:
            os.makedirs(DATA_DIR)
    
    def RegisterWorker(self, request, context):
        
        self.lock.acquire()
        worker_address = request.address
        worker_type = request.worker_type
        
        print(f"Registration request: {worker_address} | {worker_type}")
        print(f"[MASTER]: Registering worker {worker_address}:{worker_type} at master")
        
        if(worker_address in self.workers[worker_type].keys()):
            print(" |-> Worker already registered.")
            self.lock.release()
            return map_reduce_sys_pb2.RegisterWorkerResponse(
                status="SUCCESS",
                message="Worker already registered with master"
            )
        else:
            try:
                self.workers[worker_type][worker_address] = {"status": "idle"}
                print(f"  |-> Successfully registered worker\n  |-> workers List : {self.workers}")
                self.lock.release()
                return map_reduce_sys_pb2.RegisterWorkerResponse(
                    status="SUCCESS",
                    message="Worker successfully registered with master."
                )
            except:
                print(f" |-> Failed to register worker")
                self.lock.release()
                return map_reduce_sys_pb2.RegisterWorkerResponse(
                    status="FAIL",
                    message="Failed to register worker with master."
                )
    
    def MapWorkerNotification(self, request, context):
        
        worker_address = request.worker_address
        status = request.task_status
        partition_files = request.partition_files
        
        self.lock.acquire()
        self.workers["mapper"][worker_address]["status"] = "idle" if status == "completed" else self.workers["mapper"][worker_address]["status"]
        self.task_status["map"][worker_address]["status"] = status
        self.task_status["map"][worker_address]["partition_files"] = partition_files
        self.lock.release()
        print(f"---> [MAPPER NOTIF]: Mapper {worker_address} has completed its map task\n      |-> Partition files = {partition_files}\n")
        return map_reduce_sys_pb2.MapWorkerNotificationResponse(status="SUCCESS")
    
    def ReduceWorkerNotification(self, request, context):
        
        worker_address = request.worker_address
        status = request.task_status
        reducer_local_op = request.reducer_local_output_loc
        
        self.lock.acquire()
        self.workers["reducer"][worker_address]["status"] = "idle" if status == "completed" else self.workers["reducer"][worker_address]["status"]
        self.task_status["reduce"][worker_address]["status"] = status
        self.lock.release()
        print(f"---> [REDUCER NOTIF]: Reducer {worker_address} has completed its map task\n      |-> Reducer local output = {reducer_local_op}\n")
        return map_reduce_sys_pb2.ReduceWorkerNotificationResponse(status="SUCCESS")
    
    def run_mappers(self):
        
        input_dir_cont = os.listdir(self.input_data_loc)
        input_files = list(filter(lambda x: x.find("Input") != -1, input_dir_cont))
        
        idle_mappers = self.get_idle_workers(worker_type="mapper")
        
        # assert len(idle_mappers) == self.M #TODO:Just for debugging, later remove ?
        mapper_workers = idle_mappers[:self.M]
        # mapper_workers = random.sample(idle_mappers, k=self.M)
        print(f"-> Mapper Workers = {mapper_workers}\n")

        input_splits = {f"mapper_{i}":{"address": mapper_workers[i - 1], "assigned_splits": []} for i in range(1,self.M + 1)}
        for i in range(1, len(input_files) + 1):
            mapper_num = (i % self.M) if ((i % self.M) != 0) else self.M
            input_splits[f"mapper_{mapper_num}"]["assigned_splits"].append(os.path.join(self.input_data_loc, input_files[i - 1]))
        print(f"-> Assigned input Splits = {input_splits}\n")
        
        to_del = []
        for mapper_num in input_splits.keys():
            if(len(input_splits[mapper_num]["assigned_splits"]) == 0):
                to_del.append(mapper_num)
        
        for del_key in to_del:
            del input_splits[del_key]
        
        for mapper in input_splits.keys():
            mapper_addr = input_splits[mapper]["address"]
            self.task_status["map"][mapper_addr] = {}
            assign_map_task_request = map_reduce_sys_pb2.MapTaskAssignmentRequest(
                assigned_input_splits=input_splits[mapper]["assigned_splits"],
                R=self.R
            )
            with grpc.insecure_channel(mapper_addr) as channel:
                mapper_stub = map_reduce_sys_pb2_grpc.MapperServiceStub(channel)
                assign_map_task_response = mapper_stub.MapTaskAssignment(assign_map_task_request)
                if(assign_map_task_response.status == "SUCCESS"):
                    self.lock.acquire()
                    self.workers["mapper"][mapper_addr]["status"] = "running"
                    self.task_status["map"][mapper_addr]["status"] = "running"
                    self.lock.release()
                else:
                    raise Exception(f"Could not start map task at {mapper_addr}. Please re-run the program.") #TODO: Just for debugging remove later
        print("-> Successfully assigned map task to all mappers")            
    
    def run_reducers(self):
        
        idle_reducers = self.get_idle_workers(worker_type="reducer")
        # print(f"Idle workers = {idle_reducers}")
        
        # assert len(idle_reducers) == self.R #TODO:Just for debugging, later remove ?
        # reducer_workers = random.sample(idle_reducers, k=self.R)
        reducer_workers = idle_reducers[:self.R]
        
        print(f"-> Reducer Workers = {reducer_workers}\n")
        
        reducer_partitions = {f'reducer_{i}': {"address": reducer_workers[i - 1], "assigned_partitions": []} for i in range(1, self.R + 1)}    
        for mapper_addr in self.task_status["map"].keys():
            self.lock.acquire()
            mapper_info = self.task_status["map"][mapper_addr]
            mapper_partition_files = mapper_info["partition_files"]
            for partition_file_path in mapper_partition_files:
                partition_num = int(partition_file_path[partition_file_path.find('.txt') - 1])
                reducer_partitions[f'reducer_{partition_num}']["assigned_partitions"].append(partition_file_path)
            self.lock.release()
        
        print(f"-> Reducer assigned partitions = {reducer_partitions}\n")

        for reducer in reducer_partitions.keys():
            reducer_num = int(reducer[-1])
            self.lock.acquire()
            reducer_addr = reducer_partitions[reducer]["address"]
            assigned_partitions_reducer = reducer_partitions[reducer]["assigned_partitions"]
            self.task_status["reduce"][reducer_addr] = {}
            self.lock.release()
            reduce_task_assignment_request = map_reduce_sys_pb2.ReduceTaskAssignmentRequest(
                assigned_partitions=assigned_partitions_reducer,
                reducer_num = reducer_num,
                output_data_loc=self.output_data_loc
            )
            # print(f"ReduceTaskAssignmentRequest : {reduce_task_assignment_request}\n")
            with grpc.insecure_channel(reducer_addr) as channel:
                reducer_stub = map_reduce_sys_pb2_grpc.ReducerServiceStub(channel)
                reduce_task_assignment_response = reducer_stub.ReduceTaskAssignment(reduce_task_assignment_request)
                if(reduce_task_assignment_response.status == "SUCCESS"):
                    self.lock.acquire()
                    self.workers["reducer"][reducer_addr]["status"] = "running"
                    self.task_status["reduce"][reducer_addr]["status"] = "running"
                    self.lock.release()
                else:
                    raise Exception(f"Could not start reduce task at {reducer_addr}. Please re-run the program.") #TODO: Just for debugging remove later
        print("-> Successfully assigned reduce task to all reducers") 
    
    def get_idle_workers(self, worker_type):
        self.lock.acquire()
        idle_workers = []
        for worker_addr in self.workers[worker_type]:
            if(self.workers[worker_type][worker_addr]["status"] == "idle"):
                idle_workers.append(worker_addr)
        self.lock.release()
        return idle_workers

    def check_task_status(self, task_type):
        self.lock.acquire()
        for worker_addr in self.task_status[task_type].keys():
            if(self.task_status[task_type][worker_addr]["status"] == "running"):
                self.lock.release()
                return False
        self.lock.release()
        return True
            
    
    def __str__(self):
        master_details = {"address": self.address, "M": self.M, "R": self.R, "input_data_loc":self.input_data_loc, "output_loc": self.output_data_loc}
        return str(master_details)
    
if __name__ == "__main__":
    
    print("Provide the following details to master (absolute path)")
    inp_config_loc = input("Config file location (has details of 'M' and 'R'): ")
    inp_input_data_loc = input("Input Data Location: ")
    inp_output_data_loc = input("Output Data Location: ")
    
    # master_obj = Master(config_loc="C:/Users/samyj/Desktop/Sem8/DSCD/DSCD-Winter-2023/project/word_count_task/alternate_implementation/sample_files/config.txt",
    #                     input_data_loc="C:/Users/samyj/Desktop/Sem8/DSCD/DSCD-Winter-2023/project/word_count_task/alternate_implementation/sample_files",
    #                     output_data_loc="C:/Users/samyj/Desktop/Sem8/DSCD/DSCD-Winter-2023/project/word_count_task/alternate_implementation/sample_files")

    master_obj = Master(config_loc=inp_config_loc,
                        input_data_loc=inp_input_data_loc,
                        output_data_loc=inp_output_data_loc)

    grpc_master = grpc.server(futures.ThreadPoolExecutor())
    map_reduce_sys_pb2_grpc.add_MasterServiceServicer_to_server(master_obj, grpc_master)
    grpc_master.add_insecure_port(master_obj.address)
    print(master_obj)
    grpc_master.start()
    print(f"\n------------ Started MASTER at {master_obj.address} --------------------")
    
    print(f"\n ------------ Spawing mappers and reducers --------------------\n")
    time.sleep(5)
    mapper_process = []
    reducer_process = []
    
    for i in range(master_obj.M):
        mapper_process.append(Process(target=mapper.main, args=("localhost", str(5001+i), f"MAPPER_{i + 1}", 50)))
    for i in range(master_obj.R):
        reducer_process.append(Process(target=reducer.main, args=("localhost", str(6001+i), f"REDUCER_{i + 1}", 50))) 
    
    for map_proc in mapper_process:
        map_proc.start()
        time.sleep(2)
    time.sleep(2)
    for reduce_proc in reducer_process:
        reduce_proc.start()
        time.sleep(2)
    
    print("\n-------------------- Starting Map Phase --------------------\n")
    time.sleep(5)
    master_obj.run_mappers()
    while(master_obj.check_task_status("map") != True):
        time.sleep(5)
        continue
    print("\n-------------------- Map Phase Complete... Now starting Reduce Phase -----------------\n")
    time.sleep(5)
    master_obj.run_reducers()
    while(master_obj.check_task_status("reduce") != True):
        time.sleep(5)
        continue
    print("\n-------------------- Reduce Phase Complete -----------------\n")
    
    for map_proc in mapper_process:
        map_proc.join()
    time.sleep(2)
    for reduce_proc in reducer_process:
        reduce_proc.join()
    
    grpc_master.wait_for_termination(timeout=70)