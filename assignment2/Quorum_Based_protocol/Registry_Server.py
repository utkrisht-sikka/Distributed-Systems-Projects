import time
import grpc
import readwrite_sys_pb2
import readwrite_sys_pb2_grpc
import os
from concurrent import futures
from threading import Thread, Lock
from datetime import date
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from enum import Enum
import random
from Server import STATUS
import shutil
random.seed(0);

class RegistryServer(readwrite_sys_pb2_grpc.RegistryServerServiceServicer):
    def removePreviousStaleDirectories(self):
        try:
            current_directory = os.path.abspath('./');
            data_directory = "SERVER_";
            file_list = os.listdir(current_directory)
            for file_loc in file_list:
                if(os.path.isdir(os.path.join(current_directory,file_loc))):
                    if(file_loc.find(data_directory)!=-1):
                        print("file_loc={}".format(file_loc));
                        shutil.rmtree(os.path.join(current_directory,file_loc));
            new_file_list = os.listdir(current_directory)
            
            
        except Exception as arg:
            print("error occured in removing previous directories exception={}".format(arg));
    def __init__(self, N_r,N_w,N,ip="localhost", port=5555):
        self.address = ip + ":" + str(port)
        self.inmemory_map = {}
        self.server_addresses=[];
        self.lock = Lock()
        self.read_replicas = N_r;
        self.write_replicas = N_w;
        self.total_replicas = N;
        self.removePreviousStaleDirectories()
    def addServer(self, request, context):
        general_response = readwrite_sys_pb2.GeneralResponse();
        try:
            server_ip = request.ip;
            server_port = request.port;
            general_response = readwrite_sys_pb2.GeneralResponse();
            print("request for server registration server_ip={} server_port={} server_addresses={}".format(server_ip,server_port,self.server_addresses));
            if([server_ip,server_port] not in self.server_addresses):
                self.server_addresses.append([server_ip,server_port]);
                print("Server registered successfully");
                general_response.message_val = "Server registered successfully "+STATUS.SUCCESS.value;
            else:
                # print("Server already registered!");
                general_response.message_val = "Server already registered! "+STATUS.SUCCESS.value;
        except Exception as exp:
            print("Exception occured in addServer={}",exp);
            general_response.message_val = "Exception occured while adding server "+STATUS.FAILURE.value;

        return general_response;

    def getServerList(self, request, context):
        print("GetServerList request received in RegistryServer")
        for index,(ip,port) in enumerate(self.server_addresses):
            general_response = readwrite_sys_pb2.GeneralResponse();
            general_response.message_val = ip+":"+port;
            yield general_response; 
    
    def getReadServers(self,request,context):
        print("GetReadServers request received in RegistryServer");
        index_nums = random.sample(range(0, len(self.server_addresses)), self.read_replicas);
        for ind in index_nums:
            ip,port = self.server_addresses[ind];
            general_response = readwrite_sys_pb2.GeneralResponse();
            general_response.message_val = ip+":"+port;
            yield general_response; 
    
    def getWriteServers(self,request,context):
        print("GetWriteServers request received in RegistryServer");
        index_nums = random.sample(range(0, len(self.server_addresses)), self.write_replicas);
        for ind in index_nums:
            ip,port = self.server_addresses[ind];
            general_response = readwrite_sys_pb2.GeneralResponse();
            general_response.message_val = ip+":"+port;
            yield general_response; 
        print("All finished")


def main(n_r,n_w,n,timeout):
    print("In Registry_Server n_r={} n_w={} n={} timeout={}".format(n_r,n_w,n,timeout));
    try:
        assert(n_r+n_w>n and n_w>n/2);
        registry_server_object = RegistryServer(N_r=n_r,N_w=n_w,N=n,ip="localhost", port=5555)
        grpc_registry_server = grpc.server(futures.ThreadPoolExecutor())
        readwrite_sys_pb2_grpc.add_RegistryServerServiceServicer_to_server(registry_server_object, grpc_registry_server)
        grpc_registry_server.add_insecure_port(registry_server_object.address)
        print(f" ------------ Starting Registry Server at {registry_server_object.address}--------------------")
        grpc_registry_server.start()
        if(timeout != 0):
            grpc_registry_server.wait_for_termination(timeout)
        else:
            grpc_registry_server.wait_for_termination()
    except Exception as exp:
        print("error occured in main method of Registry_Server.py exp = {}".format(exp));





if __name__ == "__main__":
    tp = True;
    while tp:
        try:
            ip = "localhost";port = 5555;
            # new_ip = input("Enter the ip of Registry_Server: ")
            # new_port = int(input("Enter the ip of Registry_Server: "))

            # assert(new_ip==ip and new_port==port);
            REGISTRY_ADDRESS = ip+":"+str(port);
            N_r,N_w,N = 2,2,3;
            # N_r,N_w,N = [int(x) for x in input("Please enter the value of N_r,N_w and N in space separated format :    ").strip().split(" ")]
            assert(N_r+N_w>N and N_w>N/2);
            tp = False;
        except Exception as arg:
            print("Exception occured={} \n Constraints aren't satisfied , Please try again with valid values of N_r,N_w and N such that N_r+N_w>N".format(arg));


    
    
    registry_server_object = RegistryServer(N_r,N_w,N);
    print("registry server address={}".format(ip,port))
    # try:
    with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
        grpc_server = grpc.server(futures.ThreadPoolExecutor())
        readwrite_sys_pb2_grpc.add_RegistryServerServiceServicer_to_server(registry_server_object, grpc_server)
        grpc_server.add_insecure_port(registry_server_object.address)
        print(f"\n\n-------- Starting RegistryServer : {registry_server_object.address} --------\n")
        grpc_server.start()
        grpc_server.wait_for_termination()