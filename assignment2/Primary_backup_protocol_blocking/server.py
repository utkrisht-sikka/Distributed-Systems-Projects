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

REGISTRY_ADDRESS = "localhost:5555"

class Server(readwrite_sys_pb2_grpc.ServerServiceServicer):

    def create_directory(self, folder):

        current_directory = os.path.abspath('./')
        data_path = os.path.join(current_directory, folder)

        if not os.path.exists(data_path):
            try:
                os.mkdir(data_path)
                print("Directory created successfully!={}".format(data_path))
            except Exception as exp:
                print("Exception occured while creating directory={} exp={}",data_path,exp)
        else:
            raise BaseException(f"Directory already exists for server={data_path}")
        
        return data_path
                                
    def __init__(self, ip, port, folder):
        self.ip = ip
        self.port = port
        self.address = ip + ":" + str(port)
        self.inmemory_map = {}
        self.directory_replica = self.create_directory(folder)
        self.lock = Lock()
        self.lockrwd = Lock()
        self.isPrimary = False
        self.replicas = None
        self.primary_server_address = None
    

    def register_server(self, stub):
        registration_request = readwrite_sys_pb2.RegisterServerRequest(
            address=self.address
        )
        registration_response = stub.RegisterServer(registration_request)
        
        print(f"Server registration : {registration_response.status}, {registration_response.message}")
        
        if(registration_response.status == "SUCCESS"):
            self.primary_server_address = registration_response.primaryServerAddress
            if((self.isPrimary == False) and (self.primary_server_address == self.address)):
                print("Setting server as primary replica!")
                self.isPrimary = True
                self.replicas = []          
        return registration_response

    def NotifyPrimary(self, request, context):
        replica_address = request.replicaAddress
        
        self.lock.acquire()
        try:
            self.replicas.append(replica_address)
            print(f"Primary: New replica - {replica_address} registered with registry.")
            print(f" |-> Replicas: {self.replicas}")
            self.lock.release()
            notify_primary_response = readwrite_sys_pb2.NotifyPrimaryResponse(
                status="SUCCESS",
                message=f"Primary Server notified of replica ({replica_address}) registration"
            )
            return notify_primary_response
        except:
            self.lock.release()
            notify_primary_response = readwrite_sys_pb2.NotifyPrimaryResponse(
                status="FAIL",
                message=f"Couldn't notify Primary Server replica ({replica_address}) registration"
            )
            return notify_primary_response

    def fileio(self, request):
        file = open(os.path.join(self.directory_replica, request.Name), 'w')
        file.write(request.Content)
        file.close()

   
    
    def write_PRtoRepl(self, request, context):
        # print(f"\nName : {request.Name}")
        # print(f"Content : {request.Content}")
        # print(f"uuid : {request.uuid}")
        
        response = readwrite_sys_pb2.WritePRtoReplResponse()      
        self.lockrwd.acquire()
        self.inmemory_map[request.uuid] = (request.Name, request.Version)
        self.fileio(request)
        self.lockrwd.release()
        response.Status = "SUCCESS"
        return response

    def write(self, request, context):
        
        # print(f"\nName : {request.Name}")
        # print(f"Content : {request.Content}")
        # print(f"uuid : {request.uuid}")
        if(not self.isPrimary):
            # try:
            with grpc.insecure_channel(self.primary_server_address) as channel:
                    server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                    write_response = server_stub.write(request)
                    # print(f"->Status : {write_file_response.Status}")
                    # print(f"->uuid : {write_file_response.uuid}")
                    # print(f"->Version : {write_file_response.Version}")
            # except:
            #     print("Could not connect to the Primary server.")
            
            return write_response
        
        write_response = readwrite_sys_pb2.WriteResponse()
        self.lockrwd.acquire()
        bool1 = request.uuid in self.inmemory_map
        bool2 = self.search_filename(request.Name)
        if(bool1 and bool2):
            bool3 = (self.inmemory_map[request.uuid][0] == request.Name)
        self.lockrwd.release()
        if((not bool1) and (not bool2)):
            received_timestamp = Timestamp()
            dn = datetime.now()
            received_timestamp.FromDatetime(dn)
            self.lockrwd.acquire()
            self.inmemory_map[request.uuid] = (request.Name, received_timestamp)
            self.fileio(request)
            self.lockrwd.release()
            write_PRtoRepl_request = readwrite_sys_pb2.WritePRtoReplRequest()
            write_PRtoRepl_request.Name = request.Name
            write_PRtoRepl_request.Content = request.Content
            write_PRtoRepl_request.uuid = request.uuid
            write_PRtoRepl_request.Version.FromDatetime(dn) 
            for addr in self.replicas:
                try:
                    with grpc.insecure_channel(addr) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        write_PRtoRepl_response = server_stub.write_PRtoRepl(write_PRtoRepl_request)
                        # print(f"->Status : {write_PRtoRepl_response.Status}")
                        
                except:
                    print("Primary could not forward the write.")
            write_response.Status = "SUCCESS"
            write_response.uuid = request.uuid
            write_response.Version.FromDatetime(dn) 

        elif((not bool1) and  bool2):
            write_response.Status = "FILE WITH THE SAME NAME ALREADY EXISTS"
            write_response.uuid = "None"
            write_response.Version.FromDatetime(datetime.min)

        elif( bool1 and bool2):
            if(bool3):
                # print("updating...")
                received_timestamp = Timestamp()
                dn = datetime.now()
                received_timestamp.FromDatetime(dn)
                self.lockrwd.acquire()
                self.inmemory_map[request.uuid] = (request.Name, received_timestamp)
                self.fileio(request)
                self.lockrwd.release()


                write_PRtoRepl_request = readwrite_sys_pb2.WritePRtoReplRequest()
                write_PRtoRepl_request.Name = request.Name
                write_PRtoRepl_request.Content = request.Content
                write_PRtoRepl_request.uuid = request.uuid
                write_PRtoRepl_request.Version.FromDatetime(dn)
                for addr in self.replicas:
                    try:
                        with grpc.insecure_channel(addr) as channel:
                            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                            write_PRtoRepl_response = server_stub.write_PRtoRepl(write_PRtoRepl_request)
                            # print(f"->Status : {write_PRtoRepl_response.Status}")
                            
                    except:
                        print("Primary could not forward the write.")
                write_response.Status = "SUCCESS"
                write_response.uuid = request.uuid
                write_response.Version.FromDatetime(dn)

            else:
                write_response.Status = "UUID AND FILENAME DO NOT MATCH"
                write_response.uuid = "None"
                write_response.Version.FromDatetime(datetime.min)  

        elif( bool1 and (not bool2)):
            write_response.Status = "DELETED FILE CANNOT BE UPDATED"
            write_response.uuid = "None"
            write_response.Version.FromDatetime(datetime.min) 

        
        else:
            #unknown scenario
            pass
        return write_response
    
    def search_filename(self, name):
        if os.path.isfile(os.path.join(self.directory_replica, name)):
            return True
        return False

    def search_file(self, Uuid):
        filename, timestamp = self.inmemory_map[Uuid]
        if os.path.isfile(os.path.join(self.directory_replica, filename)):
            return True
        return False
     
    def read(self, request, context):
        # print(f"uuid : {request.uuid}")
        
        read_file_response = readwrite_sys_pb2.ReadResponse()
        self.lockrwd.acquire()
        # time.sleep(10)

        if(request.uuid not in self.inmemory_map):
            read_file_response.Status = "FILE DOES NOT EXIST"
            read_file_response.Name = "None"
            read_file_response.Content = "None"
            read_file_response.Version.FromDatetime(datetime.min)

        elif(self.search_file(request.uuid)):
            filename, timestamp = self.inmemory_map[request.uuid]
            read_file_response.Status = "SUCCESS"
            read_file_response.Name = filename
             
            file = open(os.path.join(self.directory_replica, filename),"r")

            read_file_response.Content = file.read()
            file.close()
            d = timestamp.ToDatetime()            
            read_file_response.Version.FromDatetime(d)

        else:
            read_file_response.Status = "FILE ALREADY DELETED"
            filename, timestamp = self.inmemory_map[request.uuid]
            read_file_response.Name = filename
            read_file_response.Content = "None"
            d = timestamp.ToDatetime()            
            read_file_response.Version.FromDatetime(d)
        
        self.lockrwd.release()
        return read_file_response
    
    def delfile(self, request):
        filename, timestamp = self.inmemory_map[request.uuid]
        # print(self.inmemory_map)
        os.remove(os.path.join(self.directory_replica, filename))



    def delete_PRtoRepl(self, request, context):
        # print(f"uuid : {request.uuid}")
        response = readwrite_sys_pb2.DeleteResponse()
        self.lockrwd.acquire()
        self.delfile(request)
        self.inmemory_map[request.uuid] = ("", request.Version)
        self.lockrwd.release()
        response.Status = "SUCCESS"

        return response

    def delete(self, request, context):
        if(not self.isPrimary):
            try:
                with grpc.insecure_channel(self.primary_server_address) as channel:
                        server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                        delete_response = server_stub.delete(request)
                        
            except:
                print("Could not connect to the Primary server.")
            return delete_response

        delete_response = readwrite_sys_pb2.DeleteResponse()
        self.lockrwd.acquire()
        
        bool1 = request.uuid in self.inmemory_map
        self.lockrwd.release()

        if(not bool1):
            delete_response.Status = "FILE DOES NOT EXIST"
        else:
            self.lockrwd.acquire()
            bool2 = self.search_file(request.uuid)
            self.lockrwd.release()
            if(bool2):
              
                received_timestamp = Timestamp()
                dn = datetime.now()
                received_timestamp.FromDatetime(dn)
                self.lockrwd.acquire()
                self.delfile(request)
                self.inmemory_map[request.uuid] = ("", received_timestamp)                   
                self.lockrwd.release()

                request_PRtoRepl = readwrite_sys_pb2.DeletePRtoRepl()
                request_PRtoRepl.uuid = request.uuid
                request_PRtoRepl.Version.FromDatetime(dn)
                for addr in self.replicas:
                    try:
                        with grpc.insecure_channel(addr) as channel:
                            server_stub = readwrite_sys_pb2_grpc.ServerServiceStub(channel)
                            response = server_stub.delete_PRtoRepl(request_PRtoRepl)
                            # print(f"->Status : {response.Status}")
                        
                    except:
                        print("Primary could not forward the delete.")
                
                    
                delete_response.Status = "SUCCESS"
            else:
                delete_response.Status = "FILE ALREADY DELETED"

        return delete_response


# if __name__ == "__main__":
def main(ip, port, directory, timeout):
    
    # print("Please enter the details of the server")
    # ip = input("IP : ")
    # ip = "localhost"
    # port = input("Port : ")
    # port = "5556"
    # directory = input("Directory of Replica : ")
    # directory = r"C:\Ddrive\classroom\sem8\DSCD\assignment2\Primary_backup_protocol_blocking\s1"
    server_object = Server(ip, port, directory)
    
    if(server_object.address == "localhost:5555"):
        print("Cannot take the address of Registry Server")
    
    else:
        print(f"---> DEPLOYING SERVER {server_object.address}")
        with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
            registry_stub = readwrite_sys_pb2_grpc.RegistryServiceStub(channel)
            registration_response = server_object.register_server(registry_stub)
            if(registration_response.status == "SUCCESS"):
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
