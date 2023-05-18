import grpc
import map_reduce_sys_pb2
import map_reduce_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import os
import shutil
import random
import time
import mapper, reducer
from multiprocessing import Process

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
        self.interim_data_loc, self.partitions = {}, {}
        self.output_data_loc = output_data_loc
        self.mappers, self.reducers = {}, {}
        if(os.path.isdir(DATA_DIR)):
            dir_contents = os.listdir(DATA_DIR)
            for obj in dir_contents:
                if(os.path.isdir(os.path.join(DATA_DIR, obj)) and (("MAPPER_" in obj) or (("REDUCER_" in obj))) ):
                    shutil.rmtree(os.path.join(DATA_DIR, obj))
        else:
            os.makedirs(DATA_DIR)
    
    def Register(self, request, context):
        
        self.lock.acquire()
        worker_address = request.address
        
        print(f"[MASTER]: Registering {request.name} at master")
        
     
        try:
            if(request.name.startswith("MAPPER_")):
                self.mappers[worker_address] = {"status": "idle",  "name":request.name}
            elif(request.name.startswith("REDUCER_")):
                self.reducers[worker_address] = {"status": "idle", "name":request.name}
            else:
                pass

            print(f"  |-> Successfully registered")
            self.lock.release()
            return map_reduce_sys_pb2.Response(
                status="SUCCESS",
                message="Successfully registered with master."
            )
        except:
            print(f" |-> Failed to register")
            self.lock.release()
            return map_reduce_sys_pb2.Response(
                status="FAIL",
                message="Failed to register with master."
            )

    def MapperDone(self, request, context):
        self.lock.acquire()
        name = self.mappers[request.address]["name"]
        print(f"Mapper {request.address} {name} completed\n")
        print("Intermediate Files\n")
        for i in request.interim_files:
            print(i)
        print("\n")
        self.mappers[request.address]["status"] = "completed"
        self.interim_data_loc[request.address] = request.interim_files
       
        self.partitions[request.address] = request.partitions
        self.lock.release()
        return map_reduce_sys_pb2.Response(
            status="SUCCESS",
            message="Notified successfully"
        )
         

    def run_mappers(self):
        
        input_dir_cont = os.listdir(self.input_data_loc)
        input_files = list(filter(lambda x: x.find("Input") != -1, input_dir_cont))
        docID = {}

        print(f"Input Files : {input_files}")      

        mapper_workers = []
        for i in self.mappers:
            mapper_workers.append(i)
        print(f"Mapper Workers = {mapper_workers}")
        
        
        reducer_workers = []
        for i in self.reducers:
            reducer_workers.append(i)
        print(f"Reducer Workers = {reducer_workers}")

         

        input_splits = {f"MAPPER_{i}":{"address": mapper_workers[i - 1], "assigned_splits": [], "DocIDs" : []} for i in range(1,self.M + 1)}
        
        for i in range(1, len(input_files) + 1):
            mapper_num = (i % self.M) if ((i % self.M) != 0) else self.M
            curdir = os.path.abspath("./")
            curdir = os.path.join(curdir, "sample_files")
            curdir = os.path.join(curdir, input_files[i - 1])

            input_splits[f"MAPPER_{mapper_num}"]["assigned_splits"].append(curdir)
            input_splits[f"MAPPER_{mapper_num}"]["DocIDs"].append(i)

        toremove = []
        for mapper in input_splits.keys():
            if(len(input_splits[mapper]["DocIDs"]) == 0):
                toremove.append(mapper)
        for mapper in toremove:
            del input_splits[mapper]

        print(f"Map Task Assignment Strategy :\n")
        for i in input_splits.keys():
            print(i)
            print(input_splits[i])
        print("\n\n")

        print("--------Assigning Map Tasks--------\n")

        for mapper in input_splits.keys():
           
            mapper_addr = input_splits[mapper]["address"]
            assign_map_task_request = map_reduce_sys_pb2.MapTaskAssignmentRequest(
                assigned_input_splits=input_splits[mapper]["assigned_splits"],
                DocIDs=input_splits[mapper]["DocIDs"],
                R = self.R
            )
            with grpc.insecure_channel(mapper_addr) as channel:
                worker_stub = map_reduce_sys_pb2_grpc.MapperServiceStub(channel)
                assign_map_task_response = worker_stub.MapTaskAssignment(assign_map_task_request)
                if(assign_map_task_response.status == "SUCCESS"):
                    self.mappers[mapper_addr]["status"] = "running"
                else:
                    raise Exception(f"Could not start map task at {mapper_addr}") #TODO: Just for debugging remove later
        

        # wait for mappers to complete
        while(1):
            alldone = True
            for addr in self.mappers:
                if(self.mappers[addr]["status"] == "running"):
                    alldone = False
            if(alldone):
                break
            
        print("--------All mappers completed--------\n")
        
    def ReducerDone(self, request, context):
        self.lock.acquire()
        name = self.reducers[request.address]["name"]
        print(f"Reducer {request.address} {name} completed\n")
        print("Output File\n")
        print(request.interim_files)
        print("\n")
        self.reducers[request.address]["status"] = "completed"
        self.lock.release()
        return map_reduce_sys_pb2.Response(
            status="SUCCESS",
            message="Notified successfully"
        )
    
    def run_reducers(self):
        reducer_workers = []
        for i in self.reducers:
            reducer_workers.append(i)

        assign_files = []
        for i in range(self.R):
            assign_files.append([])

        for key in self.interim_data_loc:
            i=0
            for file in self.interim_data_loc[key]:
                idx = self.partitions[key][i]
                assign_files[idx].append(file)
                i+=1

        print(f"Reduce Task Assignment Strategy :\n")
        i=0
        for addr in reducer_workers:
            print(f"Reducer {addr} {self.reducers[addr]['name']} will be given Partition {i}")
            print(f"Intermediate Partitioned Files\n")
            for file in assign_files[i]: 
                print(file)
            i+=1
            print("\n")
            if(i == self.R):
                break
        print("--------Assigning Reduce Task--------\n")    
        i=0
        for addr in reducer_workers:
            assign_reduce_task_request = map_reduce_sys_pb2.ReduceTaskAssignmentRequest(
                assigned_interim_files = assign_files[i],
                output_data_loc = self.output_data_loc
            )

            with grpc.insecure_channel(addr) as channel:
                worker_stub = map_reduce_sys_pb2_grpc.ReducerServiceStub(channel)
                assign_reduce_task_response = worker_stub.ReduceTaskAssignment(assign_reduce_task_request)
                if(assign_reduce_task_response.status == "SUCCESS"):
                    self.reducers[addr]["status"] = "running"
                else:
                    raise Exception(f"Could not start reduce task at {i} {reducer_workers[addr]['name']}") #TODO: Just for debugging remove later
            i+=1
            if(i == self.R):
                break

        
        while(1):
            alldone = True
            for addr in self.reducers:
                if(self.reducers[addr]["status"] == "running"):
                    alldone = False
            if(alldone):
                break
            
        print("--------All reducers completed--------\n")
        
    def __str__(self):
        master_details = {"address": self.address, "M": self.M, "R": self.R, "input_data_loc":self.input_data_loc}
        return str(master_details)
    
if __name__ == "__main__":
    current_directory = os.path.abspath("./")
    data_path = os.path.join(current_directory, "sample_files")
    config_path = os.path.join(data_path, "config.txt")

    master_obj = Master(config_loc=config_path,
                        input_data_loc=data_path,
                        output_data_loc=data_path)

    grpc_master = grpc.server(futures.ThreadPoolExecutor())
    map_reduce_sys_pb2_grpc.add_MasterServiceServicer_to_server(master_obj, grpc_master)
    grpc_master.add_insecure_port(master_obj.address)
    print(f" ------------ Starting Master at {master_obj.address}--------------------")
    print(master_obj)
    print("\n\n")
    
    grpc_master.start()
    
    time.sleep(2)
    #spawn processes
    s = []
    for i in range(1, master_obj.M + 1):
        s.append(Process(target = mapper.main, args=("localhost", str(5556+i),  r"MAPPER_"+str(i), 45,)))
        
    for i in range(1, master_obj.R + 1):
        s.append(Process(target = reducer.main, args=("localhost", str(5556+i+master_obj.M),  r"REDUCER_"+str(i), 45,)))

    for i in s:
        i.start()
        time.sleep(2)
    
    master_obj.run_mappers()
    master_obj.run_reducers()
    
    for i in s:
        i.join()

    grpc_master.wait_for_termination()