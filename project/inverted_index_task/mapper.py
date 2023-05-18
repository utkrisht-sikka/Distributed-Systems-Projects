import grpc
import map_reduce_sys_pb2
import map_reduce_sys_pb2_grpc
from threading import Thread
from concurrent import futures
from threading import Thread, Lock
import os
import shutil
import time

MASTER_ADDRESS = "localhost:5555"
DATA_DIR = os.path.join(os.getcwd(), "workers_data_dir")

class Mapper:

    def  __init__(self, ip, port, dir_path):
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        self.name = dir_path
        self.mapper_directory = os.path.join(DATA_DIR, dir_path)
        os.makedirs(self.mapper_directory)
            
        
    def register_mapper(self, stub):
        registration_request = map_reduce_sys_pb2.RegisterRequest(address=self.address, name=self.name)
        registration_response = stub.Register(registration_request)
        return registration_response
    
    def MapThread(self, request):
        R = request.R
        assigned_splits = request.assigned_input_splits
        DocIDs = request.DocIDs
        emit = []
        for i in range(len(assigned_splits)):
            f =  open(assigned_splits[i], "r") 
            emit.extend(self.mapfunc(DocIDs[i], f.read()))

        f = open(os.path.join(self.mapper_directory,"IF.txt") , "w")
        for i in emit:
            f.write(str(i[0])+","+str(i[1])+"\n")
        f.close() 

        self.partition(emit, R)
        files, parts = [], []
        for i in range(R):
            files.append(os.path.join(self.mapper_directory, "partition"+str(i)+".txt"))
            parts.append(i)

        mapperdone_request = map_reduce_sys_pb2.MapperDoneRequest(
                interim_files=files,
                address=self.address,
                partitions=parts
            )
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            master_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            response = master_stub.MapperDone(mapperdone_request)
            if(response.status == "SUCCESS"):
                pass 
            else:
                raise Exception(f"Could not notify master {MASTER_ADDRESS}") #TODO: Just for debugging remove later

        


    def MapTaskAssignment(self, request, context):
        thread = Thread(target = self.MapThread, args = (request,))
        thread.start()
     

        return map_reduce_sys_pb2.Response(
            status="SUCCESS",
            message="Assigned successfully"
        )

    def mapfunc(self, key, value):
        emit = []
        lines = value.splitlines()
        for line in lines:
            words = line.split()
            for word in words:
                low = word.lower()
                emit.append((low, key))
        return emit
    
    def hash(self, key):
        tot = 0
        for i in key:
            tot += ord(i)
        
        return tot

    def partition(self, emit, R):
        
        files = []
        for i in range(R):
            files.append(open( os.path.join(self.mapper_directory,"partition"+str(i)+".txt") , "w"))
        for i in emit:
            part = self.hash(i[0])%R
            files[part].write(str(i[0])+","+str(i[1])+"\n")
        
        for i in files:
            i.close() 

    
       

    

def main(ip, port, dir_name, timeout):
# if __name__ == "__main__":
    
    # print("Please enter the details of the worker")
    # ip = input("IP : ")
    # port = input("Port : ")
    # dir_name = input("Directory name: ")
    
    mapper_obj = Mapper(ip, port, dir_name)
    
    if(mapper_obj.address == "localhost:5555"):
        print("Address already taken by master")
    
    else:
        print(f"---> DEPLOYING Mapper {mapper_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = mapper_obj.register_mapper(registry_stub)
            print(f"Mapper registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_mapper = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_MapperServiceServicer_to_server(mapper_obj, grpc_mapper)
                grpc_mapper.add_insecure_port(mapper_obj.address)
                print(f"\n\n-------- Starting Mapper : {mapper_obj.address} --------\n")
                grpc_mapper.start()
                if(timeout != 0):
                    grpc_mapper.wait_for_termination(timeout)
                else:
                    grpc_mapper.wait_for_termination()
                
            else:
                print(f" -------- Failed to start Mapper --------")
            