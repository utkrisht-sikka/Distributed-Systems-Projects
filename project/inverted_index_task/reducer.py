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

class Reducer:

    def  __init__(self, ip, port, dir_path):
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        self.name = dir_path
        self.reducer_directory = os.path.join(DATA_DIR, dir_path)
        os.makedirs(self.reducer_directory)
            
        
    def register_reducer(self, stub):
        registration_request = map_reduce_sys_pb2.RegisterRequest(address=self.address, name=self.name)
        registration_response = stub.Register(registration_request)
        return registration_response
    
    

    def ReduceThread(self, request):

        k_v = self.sort(request.assigned_interim_files)

        kv_agg = {}
        for i in k_v:
            if(i[0] in kv_agg):
                kv_agg[i[0]].add(i[1])
            else:
                kv_agg[i[0]] = set([i[1]])
        
        file =  os.path.join(self.reducer_directory, "Output.txt")
        file2 =  os.path.join(request.output_data_loc, "Output"+self.name+".txt")

        fpt = open(file, "w")
        fpt2 = open(file2, "w")

        for key in kv_agg:
            x = self.reduce(key, kv_agg[key])
            values = list(x[1])
            line = str(x[0]) + " " + str(values[0])
            for idx in range(1, len(values)):
                line += ", " + str(values[idx])
            line += "\n"
            fpt.write(line)
            fpt2.write(line)
        
        fpt.close()
        fpt2.close()

        reducerdone_request = map_reduce_sys_pb2.ReducerDoneRequest(
                interim_files=file,
                address=self.address
            )
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            master_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            response = master_stub.ReducerDone(reducerdone_request)
            if(response.status == "SUCCESS"):
                pass 
            else:
                raise Exception(f"Could not notify master {MASTER_ADDRESS}") #TODO: Just for debugging remove later



    def sort(self, files):
        k_v = []
        for file in files:
            f = open(file, "r")
            listt = f.read().splitlines()
            for i in listt:
                w, docid = i.split(",")
                k_v.append((w,docid))

        k_v = sorted(k_v, key = lambda x: x[0])
        return k_v

    def reduce(self, key, values):
        return (key, values)
        

    def ReduceTaskAssignment(self, request, context):
        thread = Thread(target = self.ReduceThread, args = (request,))
        thread.start()
        return map_reduce_sys_pb2.Response(
            status="SUCCESS",
            message="Assigned successfully"
        )
       

    

def main(ip, port, dir_name, timeout):
# if __name__ == "__main__":
    
    # print("Please enter the details of the worker")
    # ip = input("IP : ")
    # port = input("Port : ")
    # dir_name = input("Directory name: ")
    
    reducer_obj = Reducer(ip, port, dir_name)
    
    if(reducer_obj.address == "localhost:5555"):
        print("Address already taken by master")
    
    else:
        print(f"---> DEPLOYING Reducer {reducer_obj.address}")
        with grpc.insecure_channel(MASTER_ADDRESS) as channel:
            registry_stub = map_reduce_sys_pb2_grpc.MasterServiceStub(channel)
            registration_response = reducer_obj.register_reducer(registry_stub)
            print(f"Reducer registration : [{registration_response.status}], {registration_response.message}")
            if(registration_response.status == "SUCCESS"):
                grpc_reducer = grpc.server(futures.ThreadPoolExecutor())
                map_reduce_sys_pb2_grpc.add_ReducerServiceServicer_to_server(reducer_obj, grpc_reducer)
                grpc_reducer.add_insecure_port(reducer_obj.address)
                print(f"\n\n-------- Starting Reducer : {reducer_obj.address} --------\n")
                grpc_reducer.start()
                if(timeout != 0):
                    grpc_reducer.wait_for_termination(timeout)
                else:
                    grpc_reducer.wait_for_termination()
                
            else:
                print(f" -------- Failed to start Reducer --------")
            