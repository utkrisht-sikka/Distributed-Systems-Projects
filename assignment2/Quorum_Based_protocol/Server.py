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

class STATUS(Enum):
    SUCCESS = "SUCCESS";
    FAILURE = "FAILURE";


REGISTRY_ADDRESS = "localhost:5555"



class Server(readwrite_sys_pb2_grpc.ServerServiceServicer):
    def create_directory(self):
        current_directory = os.path.abspath('./');
        data_directory = self.folder_name;
        # new_int = random.randint(1,100);
        # if(os.path.exists(os.path.join(current_directory,data_directory+str(new_int)))):
        #     new_int = random.randint(1,100);
        data_path = os.path.join(current_directory,data_directory);

        if not os.path.exists(data_path):
            try:
                os.mkdir(data_path)
                print("Directory created successfully!={}".format(data_path))
            except Exception as exp:
                print("Exception occured while creating directory={} exp={}",data_path,exp);
        else:
            raise BaseException(f"Directory already exists for server={data_path}");
        return data_path;
        
    def add_server(self):
        add_server_response = "NULL";
        try:
            with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
                registry_server_stub = readwrite_sys_pb2_grpc.RegistryServerServiceStub(channel)
                add_server_request = readwrite_sys_pb2.AddServerRequest();
                add_server_request.ip,add_server_request.port = self.address.split(":");
                add_server_response = registry_server_stub.addServer(add_server_request);
                print("Response received in addServer response={} for address={}".format(add_server_response,self.address));

        except Exception as exp:
            print("error occured in addServer method address={} exception={}".format(self.address,exp));
        print("add_server_response={}".format(add_server_response));
        return add_server_response;


    def __init__(self, ip, port,folder_name):
        self.address = ip + ":" + str(port)
        self.folder_name = folder_name
        self.port = str(port)
        self.inmemory_map = {}
        
        self.lock = Lock()
        self.is_primary_replica = False
        self.directory_replica = self.create_directory();
        # self.add_server();
    
    def write(self, request, context):
        print("req received")
        # print("server_name={} server_ip={} server_port={}".format(request.name,request.ip,request.port))
        write_file_response = readwrite_sys_pb2.WriteResponse();
        self.lock.acquire();
        try:
            name,content,req_uuid = request.name,request.content,request.uuid;
            file_path = os.path.join(self.directory_replica,name);
            bool1 = req_uuid in self.inmemory_map
            bool2 = self.search_filename(name);
            print("bool1=={} bool2={} self.inmemory_map={} \n name={} uuid={}".format(bool1,bool2,self.inmemory_map,name,req_uuid));
            if(((not bool1) and (not bool2)) or (bool1 and bool2 and self.inmemory_map[req_uuid][0]==name)):
                # case of new file
                print("file_path={}".format(file_path));
                file = open(file_path, "w");
                file.write(content);
                write_file_response.status = STATUS.SUCCESS.value;
                write_file_response.uuid = req_uuid;
                timestamp = datetime.now();
                
                write_file_response.version.FromDatetime(timestamp);
                self.inmemory_map[req_uuid] = [name,timestamp];
            elif((not bool1) and  bool2):
                write_file_response.status = "FILE WITH THE SAME NAME ALREADY EXISTS"
                write_file_response.uuid = "None"
                write_file_response.version.FromDatetime(datetime.now())
            elif( bool1 and (not bool2)):
                write_file_response.status = "DELETED FILE CANNOT BE UPDATED"
                write_file_response.uuid = "None"
                write_file_response.version.FromDatetime(datetime.now())
            elif(bool1 and bool2):
                write_file_response.status = "WRONG MAPPING AS THE MENTIONED FILE UUID IN REQUEST IS ALREADY MAPPED TO ANOTHER FILE";
                write_file_response.uuid = "None"
                write_file_response.version.FromDatetime(datetime.now())

            
        except Exception as exp:
            print("Exception occured while writing content to replica={} exp={}",self.directory_replica,exp);
            write_file_response.status = STATUS.FAILURE.value;
            timestamp = datetime.now();
            
            write_file_response.version.FromDatetime(timestamp);
            write_file_response.uuid = "None";
        finally:
            # file.close();
            try:
                file.close();
                
            except:
                tp=2;
            # 

            #todo
        self.lock.release();
        return write_file_response
            
    def search_file(self, uuid):
        print("in search_file")
        if(uuid in self.inmemory_map):
            filename, timestamp = self.inmemory_map[uuid]
            if os.path.isfile(os.path.join(self.directory_replica, filename)):
                return True

        return False
    def search_filename(self, name):
        print("in search_filename")
        for temp in self.inmemory_map:
            if(self.inmemory_map[temp][0]==name):
                return True;


        return False
    
    def delete_file(self,uuid):
        isFilePresent = self.search_file(uuid);
        print("isFilePresent={} in method delete_file".format(isFilePresent));
        if(isFilePresent):
            path, timestamp = self.inmemory_map[uuid];
            file_path = os.path.join(self.directory_replica,path);
            try:
                os.remove(file_path)
                print("{} has been deleted.".format(path));
                timestamp_a = datetime.now();
                
                self.inmemory_map[uuid] = ["",timestamp_a]
                return True;
            except PermissionError:
                print("{} could not be deleted due to permission error.".format(path))
            except Exception as e:
                print("An error occurred while deleting {}: {}".format(path,e));
            
        else:
            print("File not present of this specific uuid currently in the directory");
            timestamp_a = datetime.now();
            # self.inmemory_map[uuid] = ["",timestamp_a];
        return False;
            

     
    def read(self, request, context):
        print("read_request_uuid={} inmemory_map={}".format(request.uuid,self.inmemory_map));
        self.lock.acquire()
        read_file_response = readwrite_sys_pb2.ReadResponse()
        uuid_req = request.uuid.strip();

        if(uuid_req not in self.inmemory_map):
            read_file_response.status = "FILE DOES NOT EXIST"+" "+STATUS.FAILURE.value;
            read_file_response.name = "None";
            read_file_response.content = "None";
            read_file_response.version.FromDatetime(datetime.now());

        elif(self.search_file(uuid_req)):

            filename, timestamp = self.inmemory_map[uuid_req];
            read_file_response.status = STATUS.SUCCESS.value;
            read_file_response.name = filename;
            file_path = os.path.join(self.directory_replica, filename);
            file = open(file_path,"r")
            read_file_response.content = file.read()
            read_file_response.version.FromDatetime(timestamp)

        else:

            read_file_response.status = "FILE ALREADY DELETED"+" "+STATUS.FAILURE.value;
            filename, timestamp = self.inmemory_map[request.uuid]
            read_file_response.name = filename
            read_file_response.content = "None"
            read_file_response.version.FromDatetime(timestamp)
        
        self.lock.release()
        return read_file_response
    def delete(self, request, context):
        print("delete_request_uuid={}".format(request.uuid));
        self.lock.acquire()
        delete_file_response = readwrite_sys_pb2.DeleteResponse()
        uuid_req = request.uuid.strip();

        if(uuid_req not in self.inmemory_map):
            delete_file_response.status = "FILE DOES NOT EXIST"+" "+STATUS.FAILURE.value;
            timestamp_a = datetime.now();
            self.inmemory_map[uuid_req] = ["",timestamp_a]

        elif(self.delete_file(uuid_req)):
            delete_file_response.status = STATUS.SUCCESS.value;

        else:
            delete_file_response.status = "FILE ALREADY DELETED"+" "+STATUS.FAILURE.value;

        self.lock.release()
        return delete_file_response

def main(ip,port,folder_name,timeout):
    server_object = Server(ip, port, folder_name);
    if(server_object.address == "localhost:5555"):
        print("Cannot take the address of Registry Server")
    
    else:
        print(f"---> DEPLOYING SERVER {server_object.address}")
        
        registration_response = server_object.add_server();
        if(registration_response.message_val.find("SUCCESS")!=-1):
            grpc_server = grpc.server(futures.ThreadPoolExecutor())
            readwrite_sys_pb2_grpc.add_ServerServiceServicer_to_server(server_object, grpc_server)
            grpc_server.add_insecure_port(server_object.address)
            print(f"\n\n-------- Starting server : {server_object.address} --------\n")
            grpc_server.start()

            if(timeout != 0):
                grpc_server.wait_for_termination(timeout)
            else:
                grpc_server.wait_for_termination()
        else:
            print(f" -------- Failed to start server : {server_object.address} --------")


# if __name__ == "__main__":
    
#     print("Please enter the details of the server")
#     ip = input("IP : ")
#     port = input("Port : ")
#     server_object = Server(ip, port)
    
#     if(server_object.address == REGISTRY_ADDRESS):
#         print("Address already taken by registry server")
    
#     else:
#         print("---> DEPLOYING SERVER")
#         print("Address={}".format(server_object.address))
#         print("Directory of Replica={}".format(server_object.directory_replica))
#         # try:
#         # with grpc.add_insecure_port('[::]:'+server_object.port) as channel:
#         grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#         readwrite_sys_pb2_grpc.add_ServerServiceServicer_to_server(server_object, grpc_server)
#         grpc_server.add_insecure_port('[::]:'+server_object.port)
#         print("\n\n-------- Starting server at directory={} address={} --------\n".format(server_object.directory_replica,server_object.address))
#         grpc_server.start()
#         grpc_server.wait_for_termination()