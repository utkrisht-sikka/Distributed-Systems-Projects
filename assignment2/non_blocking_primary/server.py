import time
import grpc
import non_blocking_sys_pb2
import non_blocking_sys_pb2_grpc
from concurrent import futures
from threading import Thread, Lock
import os
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

REGISTRY_ADDRESS = "localhost:5555"
DATA_DIR = os.path.join(os.getcwd(), "data_dir")

def get_protobuf_timestamp(get_fail=False):
    if get_fail:
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.min)
        return timestamp
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime.now())
    return timestamp

class Server(non_blocking_sys_pb2_grpc.ServerServiceServicer):
    
    def __init__(self, ip, port, directory, verbose=False):
        self.ip = ip
        self.port = port
        self.address = ip + ':' + str(port)
        self.verbose = verbose
        self.in_memory_map = {}
        self.primary_server_address = None
        self.lock = Lock()
        self.lock_rwd = Lock()
        self.isPrimary = False
        self.replicas = None
        self.directory_replica = os.path.join(DATA_DIR, directory)
        if not os.path.isdir(self.directory_replica):
            os.makedirs(self.directory_replica)
    
    def register_server(self, stub):
        
        registration_request = non_blocking_sys_pb2.RegisterServerRequest(
            address=self.address
        )
        registration_response = stub.RegisterServer(registration_request)
        
        print(f"\nServer registration : {registration_response.status}, {registration_response.message}") if self.verbose else None
        
        if(registration_response.status == "SUCCESS"):
            self.primary_server_address = registration_response.primaryServerAddress
            if((self.isPrimary == False) and (self.primary_server_address == self.address)):
                print("|-> Setting server as primary replica!") if self.verbose else None
                self.isPrimary = True
                self.replicas = []
            else:
                print(f"|-> Primary Server Address : {self.primary_server_address}") if self.verbose else None
        return registration_response

    def NotifyPrimary(self, request, context):
        
        replica_address = request.replicaAddress 
        self.lock.acquire()
        try:
            self.replicas.append(replica_address)
            print(f"\n[PRIMARY] New replica - {replica_address} registered with registry.") if self.verbose else None
            print(f" |-> Replicas: {self.replicas}") if self.verbose else None
            self.lock.release()
            notify_primary_response = non_blocking_sys_pb2.NotifyPrimaryResponse(
                status="SUCCESS",
                message=f"Primary Server notified of replica ({replica_address}) registration"
            )
            return notify_primary_response
        except:
            self.lock.release()
            notify_primary_response = non_blocking_sys_pb2.NotifyPrimaryResponse(
                status="FAIL",
                message=f"Couldn't notify Primary Server replica ({replica_address}) registration"
            )
            return notify_primary_response

    def ClientWriteReplica(self, request, context):
        
        file_name = request.name
        file_uuid = request.uuid
        file_content = request.content
        
        if(self.isPrimary == True):
            print(f"\n[PRIMARY]: WRITE request from CLIENT for file [{file_uuid}]:{file_name}") if self.verbose else None
            write_result = self.local_write(file_name, file_uuid, file_content)
            print(f"|-> STATUS: {write_result['status']}\n|   MESSAGE: {write_result['message']}") if self.verbose else None
            if(write_result["status"] == "SUCCESS"):
                print(f"|-> Propagating WRITE rquest to all replicas.")  if self.verbose else None
                background_replicas_write = Thread(target=self.write_to_all_replicas, args=(file_name, file_uuid, file_content, write_result["version"]))
                background_replicas_write.start()
                return non_blocking_sys_pb2.ClientWriteReplicaResponse(
                    status=write_result["status"],
                    uuid=write_result["uuid"],
                    version=write_result["version"]
                )
            else:
                return non_blocking_sys_pb2.ClientWriteReplicaResponse(
                    status=write_result["status"],
                    uuid=write_result["uuid"],
                    version=write_result["version"]
                )
        else:
            print(f"\n[BACKUP REPLICA]: WRITE request from CLIENT for file [{file_uuid}]:{file_name}")  if self.verbose else None
            print(f"|-> Forwarding to primary : {self.primary_server_address}")  if self.verbose else None
            with grpc.insecure_channel(self.primary_server_address) as channel:
                primary_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                forward_write_primary_request = non_blocking_sys_pb2.ForwardWritePrimaryRequest(
                    name=file_name,
                    uuid=file_uuid,
                    content=file_content
                )
                forward_write_primary_response = primary_stub.ForwardWritePrimary(forward_write_primary_request)
                print(f"|-> STATUS: {forward_write_primary_response.status}\n|   MESSAGE: {forward_write_primary_response.message}")  if self.verbose else None
                return non_blocking_sys_pb2.ClientWriteReplicaResponse(
                    status=forward_write_primary_response.status,
                    uuid=forward_write_primary_response.uuid,
                    version=forward_write_primary_response.version
                )
    
    
    def PrimaryWriteReplica(self, request, context):
        
        # assert self.isPrimary == False #TODO: Just for debugging remove it afterwards
        
        file_name = request.name
        file_uuid = request.uuid
        file_content = request.content
        file_version = request.version
        
        print(f"\n[BACKUP REPLICA]: Write file [{file_uuid}]:({file_name},{file_version.ToDatetime()}) command from primary")  if self.verbose else None
        try:
            self.lock_rwd.acquire()
            self.in_memory_map[file_uuid] = (file_name, file_version)
            self.write_to_file(file_name, file_content)
            self.lock_rwd.release()
            print(f"|-> Write successful on replica")  if self.verbose else None
            return non_blocking_sys_pb2.PrimaryWriteReplicaResponse(
                status="SUCCESS",
                message=f"Write on replica for file ({file_uuid}) successful."
            )
        except:
            print(f"|-> Write failed on replica")  if self.verbose else None
            return non_blocking_sys_pb2.PrimaryWriteReplicaResponse(
                status="FAIL",
                message=f"Write on replica for file ({file_uuid}) failed."
            )
    
    def ForwardWritePrimary(self, request, context):
        
        # assert self.isPrimary == True #TODO: Just for debugging remove it afterwards
        
        file_name =  request.name
        file_uuid =  request.uuid
        file_content = request.content
        
        print(f"\n[PRIMARY]: Forwarded write request for file ({file_uuid}) from backup")  if self.verbose else None
        
        write_result = self.local_write(file_name=file_name, file_uuid=file_uuid, file_content=file_content)
        print(f"|-> STATUS: {write_result['status']}\n|   MESSAGE: {write_result['message']}")  if self.verbose else None
        
        if(write_result["status"] == "SUCCESS"):
            print(f"|-> Propagating WRITE request to all replicas.")  if self.verbose else None
            background_replicas_write = Thread(target=self.write_to_all_replicas, args=(file_name, file_uuid, file_content, write_result["version"]))
            background_replicas_write.start()
            return non_blocking_sys_pb2.ForwardWritePrimaryResponse(
                status=write_result["status"],
                message=write_result["message"],
                uuid=write_result["uuid"],
                version=write_result["version"]
            )
        else:
            return non_blocking_sys_pb2.ForwardWritePrimaryResponse(
                status=write_result["status"],
                message=write_result["message"],
                uuid=write_result["uuid"],
                version=write_result["version"]
            )
            
    def write_to_all_replicas(self, file_name, file_uuid, file_content, file_version):
        
        # assert self.isPrimary == True  #TODO: Just for debugging remove it afterwards
        
        print(f"\n[PRIMARY]: Writing file [{file_uuid}]:({file_name},{file_version.ToDatetime()}) to all {len(self.replicas)} replicas")  if self.verbose else None
        failed_writes = []
        for replica_address in self.replicas:
            # time.sleep(10)
            with grpc.insecure_channel(replica_address) as channel:
                replica_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                primary_write_replica_request = non_blocking_sys_pb2.PrimaryWriteReplicaRequest(
                    name=file_name,
                    uuid=file_uuid,
                    content=file_content,
                    version=file_version
                )
                primary_write_replica_response = replica_stub.PrimaryWriteReplica(primary_write_replica_request)
                if(primary_write_replica_response.status == "FAIL"):
                    failed_writes.append(replica_address)
        if(len(failed_writes) == 0):
            print(f"|-> Write successful on all replicas")  if self.verbose else None
        else:
            print(f"|-> Failed to write file on the following replicas: {failed_writes}")  if self.verbose else None
                

    def local_write(self, file_name, file_uuid, file_content, file_version=None):
        
        bool_filesystem = self.search_filename(file_name) #Checks if the file exists in the filesystem
        bool_inmemory_map = file_uuid in list(self.in_memory_map.keys()) #Checks if the file exists in in_memory_map
        
        
        if(file_version == None):
            received_timestamp = get_protobuf_timestamp()
        else:
            received_timestamp = file_version
        
        if((bool_inmemory_map == False) and (bool_filesystem == False)):
            self.lock_rwd.acquire()
            self.in_memory_map[file_uuid] = (file_name, received_timestamp)
            self.write_to_file(file_name, file_content)
            self.lock_rwd.release()
            return {"status":"SUCCESS", "message": f"Created a new file [{file_uuid}]:({file_name},{received_timestamp.ToDatetime()})","uuid":file_uuid, "version":received_timestamp}
        
        elif((bool_inmemory_map == False) and (bool_filesystem == True)):
            return {"status":"[FAIL]: FILE WITH THE SAME NAME ALREADY EXISTS", "message":f"Can't create a new file with name {file_name}","uuid":"<NONE>", "version":get_protobuf_timestamp(get_fail=True)}
        
        elif((bool_inmemory_map == True) and (bool_filesystem == True)):
            self.lock_rwd.acquire()
            current_filename = self.in_memory_map[file_uuid][0]
            if(current_filename != file_name):
                self.lock_rwd.release()
                return {"status":"[FAIL]: UUID AND FILENAME DO NOT MATCH", "message":f"Filename '{file_name}' does not match with the uuid '{file_uuid}'", "uuid":"<NONE>", "version":get_protobuf_timestamp(get_fail=True)}
            self.in_memory_map[file_uuid] = (file_name, received_timestamp)
            self.write_to_file(file_name, file_content)
            self.lock_rwd.release()
            return {"status":"SUCCESS", "message":f"Updating existing file. Updated details: [{file_uuid}]:({file_name},{received_timestamp.ToDatetime()})", "uuid":file_uuid, "version":received_timestamp}
        
        elif((bool_inmemory_map == True) and (bool_filesystem == False)):
            return {"status":"[FAIL]: DELETED FILE CANNOT BE UPDATED", "message":f"Can't update deleted file [{file_uuid}]:{file_name}", "uuid":"<NONE>", "version":get_protobuf_timestamp(get_fail=True)}
    
    def ClientReadReplica(self, request, context):

        file_uuid = request.uuid
        
        print(f"\n[REPLICA]: READ request for file ({file_uuid}) from client.")  if self.verbose else None
             
        bool_inmemory_map = file_uuid in list(self.in_memory_map.keys()) #Checks if the file exists in in_memory_map
        
        if(bool_inmemory_map == False):
            print(f"|-> File does not exist") if self.verbose else None
            return non_blocking_sys_pb2.ClientReadReplicaResponse(
                status="[FAIL]: FILE DOES NOT EXIST",
                name="<NONE>",
                content="<NONE>",
                version=get_protobuf_timestamp(get_fail=True)
            )
        else:
            self.lock_rwd.acquire()
            file_name = self.in_memory_map[file_uuid][0]
            file_version = self.in_memory_map[file_uuid][1]
            self.lock_rwd.release()
            bool_filesystem = self.search_filename(file_name) #Checks if the file exists in the filesystem
            if(bool_filesystem == True):
                self.lock_rwd.acquire()
                file_contents = self.read_from_file(filename=file_name)
                self.lock_rwd.release()
                print(f"|-> File read successfully\n|   Contents = {file_contents}")  if self.verbose else None
                return non_blocking_sys_pb2.ClientReadReplicaResponse(
                    status="SUCCESS",
                    name=file_name,
                    content=file_contents,
                    version=file_version
                )
            else:
                print(f"|-> File already deleted. Deletion Time = {file_version.ToDatetime()}")  if self.verbose else None
                return non_blocking_sys_pb2.ClientReadReplicaResponse(
                    status="[FAIL]: FILE ALREADY DELETED",
                    name=file_name,
                    content="<NONE>",
                    version=file_version
                )
    
    def ClientDeleteReplica(self, request, context):
        
        file_uuid = request.uuid
        
        if(self.isPrimary == True):
            print(f"\n[PRIMARY]: DELETE request from CLIENT for file [{file_uuid}]")  if self.verbose else None
            delete_result = self.local_delete(file_uuid)
            print(f"|-> STATUS: {delete_result['status']}\n|   MESSAGE: {delete_result['message']}")  if self.verbose else None
            if(delete_result["status"] == "SUCCESS"):
                print(f"|-> Propagating DELETE rquest to all replicas.")  if self.verbose else None
                background_replicas_delete = Thread(target=self.delete_to_all_replicas, args=(file_uuid, delete_result['version']))
                background_replicas_delete.start()
                return non_blocking_sys_pb2.ClientDeleteReplicaResponse(
                    status=delete_result["status"]
                )
            else:
                return non_blocking_sys_pb2.ClientDeleteReplicaResponse(
                    status=delete_result["status"]
                )
        else:
            print(f"\n[BACKUP REPLICA]: DELETE request from CLIENT for file [{file_uuid}]")  if self.verbose else None
            print(f"|-> Forwarding to primary : {self.primary_server_address}")  if self.verbose else None
            with grpc.insecure_channel(self.primary_server_address) as channel:
                primary_stub = non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                forward_delete_primary_request = non_blocking_sys_pb2.ForwardDeletePrimaryRequest(
                    uuid=file_uuid
                )
                forward_delete_primary_response = primary_stub.ForwardDeletePrimary(forward_delete_primary_request)
                print(f"|-> STATUS: {forward_delete_primary_response.status}\n|   MESSAGE: {forward_delete_primary_response.message}")  if self.verbose else None
                return non_blocking_sys_pb2.ClientDeleteReplicaResponse(
                    status=forward_delete_primary_response.status
                )
    
    def ForwardDeletePrimary(self, request, context):
        
        # assert self.isPrimary  == True #TODO: Just for debugging remove it afterwards
        
        file_uuid = request.uuid
        
        print(f"\n[PRIMARY]: Forwarded DELETE request for file ({file_uuid}) from backup")  if self.verbose else None
        
        delete_result = self.local_delete(file_uuid=file_uuid)
        print(f"|-> STATUS: {delete_result['status']}\n|   MESSAGE: {delete_result['message']}")  if self.verbose else None
        
        if(delete_result["status"] == "SUCCESS"):
            print(f"|-> Propagating DELETE request to all replicas")  if self.verbose else None
            background_replicas_delete = Thread(target=self.delete_to_all_replicas, args=(file_uuid, delete_result['version']))
            background_replicas_delete.start()
            return non_blocking_sys_pb2.ForwardDeletePrimaryResponse(
                status=delete_result["status"],
                message=delete_result["message"]
            )
        else:
            return non_blocking_sys_pb2.ForwardDeletePrimaryResponse(
                status=delete_result["status"],
                message=delete_result["message"]
            )
    
    def PrimaryDeleteReplica(self, request, context):

        # assert self.isPrimary == False #TODO: Just for debugging remove it afterwards
        
        file_uuid =  request.uuid
        file_version = request.version
        self.lock_rwd.acquire()
        current_file_name = self.in_memory_map[file_uuid][0]
        
        print(f"\n[BACKUP REPLICA]: DELETE file [{file_uuid}]:({current_file_name}) command from primary, deletion timestamp={file_version.ToDatetime()}") if self.verbose else None
        try:
            self.delete_file(filename=current_file_name)
            self.in_memory_map[file_uuid] = ("", file_version)
            print(f"|-> DELETE successful on replica")  if self.verbose else None
            self.lock_rwd.release()
            return non_blocking_sys_pb2.PrimaryDeleteReplicaResponse(
                status="SUCCESS",
                message=f"DELETE on replica for file ({file_uuid}) successful"
            )
        except:
            self.lock_rwd.release()
            return non_blocking_sys_pb2.PrimaryDeleteReplicaResponse(
                status="FAIL",
                message=f"DELETE on replica for file ({file_uuid}) failed"
            )

    def delete_to_all_replicas(self, file_uuid, file_version):
        
        # assert self.isPrimary == True #TODO: Just for debugging remove it afterwards
        
        print(f"\n[PRIMARY]: DELETING file [{file_uuid}]:({file_version.ToDatetime()}) from all {len(self.replicas)} replicas") if self.verbose else None
        
        failed_deletes = []
        for replica_address in self.replicas:
            with grpc.insecure_channel(replica_address) as channel:
                replica_stub =  non_blocking_sys_pb2_grpc.ServerServiceStub(channel)
                primary_delete_replica_request = non_blocking_sys_pb2.PrimaryDeleteReplicaRequest(
                    uuid=file_uuid,
                    version=file_version
                )
                primary_delete_replica_response = replica_stub.PrimaryDeleteReplica(primary_delete_replica_request)
                if(primary_delete_replica_response.status == "FAIL"):
                    failed_deletes.append(replica_address)
        
        if(len(failed_deletes) == 0):
            print(f"|-> DELETE successful on all replicas") if self.verbose else None
        else:
            print(f"|-> Failed to delete file on the following replicas: {failed_deletes}") if self.verbose else None
            
            
    def local_delete(self, file_uuid):
        
        bool_inmemory_map = file_uuid in list(self.in_memory_map.keys()) #Checks if the file exists in in_memory_map
        if(bool_inmemory_map == False):
            return {"status":"[FAIL]: FILE DOES NOT EXIST", 
                    "message":f"File with uuid {file_uuid} does not exist.", 
                    "version":get_protobuf_timestamp(get_fail=True)}
        else:   
            self.lock_rwd.acquire()
            file_name = self.in_memory_map[file_uuid][0]
            file_version = self.in_memory_map[file_uuid][1]
            self.lock_rwd.release()
            bool_filesystem = self.search_filename(file_name) #Checks if the file exists in the filesystem
            
            if(bool_filesystem == True):
                self.lock_rwd.acquire()
                # time.sleep(10)
                self.delete_file(filename=file_name)
                deletion_timestamp = get_protobuf_timestamp()
                self.in_memory_map[file_uuid] = ("", deletion_timestamp)
                self.lock_rwd.release()
                return {"status":"SUCCESS", 
                        "message":f"Deleted existing file [{file_uuid}]:({file_name},{file_version.ToDatetime()}). Updated timestamp to : {deletion_timestamp.ToDatetime()}", 
                        "version":deletion_timestamp}
            else:
                return {"status": "[FAIL]: FILE ALREADY DELETED",
                        "message": f"File with uuid {file_uuid} has already been deleted at {file_version.ToDatetime()}",
                        "version": file_version}    
    
    def delete_file(self, filename):
        os.remove(os.path.join(self.directory_replica, filename))
    
    def read_from_file(self, filename):
        f = open(os.path.join(self.directory_replica, (filename)), "r")
        content = f.read()
        f.close()
        return content
        
    def write_to_file(self, filename, content):
        f = open(os.path.join(self.directory_replica, (filename)), "w")
        f.write(content)
        f.close()
    
    def search_filename(self, filename):      
        if os.path.isfile(os.path.join(self.directory_replica, (filename))):
            return True
        return False

def main(ip, port,directory_path, timeout):
    
    server_object = Server(ip, port, directory_path)    
    if(server_object.address == "localhost:5555"):
        print("Cannot take the address of Registry Server")
    
    else:
        print(f"---> DEPLOYING SERVER {server_object.address}")
        with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
            registry_stub = non_blocking_sys_pb2_grpc.RegistryServiceStub(channel)
            registration_response = server_object.register_server(registry_stub)
            if(registration_response.status == "SUCCESS"):
                grpc_server = grpc.server(futures.ThreadPoolExecutor())
                non_blocking_sys_pb2_grpc.add_ServerServiceServicer_to_server(server_object, grpc_server)
                grpc_server.add_insecure_port(server_object.address)
                print(f"\n\n-------- Starting server : {server_object.address} --------\n")
                grpc_server.start()
                if(timeout != 0):
                    grpc_server.wait_for_termination(timeout)
                else:
                    grpc_server.wait_for_termination()
            else:
                print(f" -------- Failed to start server : {server_object.address} --------")
                
if __name__ == "__main__":
    print("Please enter the details of the server")
    ip = input("IP: ")
    port = input("Port: ")
    directory_path = input("Directory: ")
    server_object = Server(ip, port, directory_path, verbose=True)
    
    if(server_object.address == "localhost:5555"):
        print("Cannot take the address of Registry Server")
    
    else:
        print(f"---> DEPLOYING SERVER {server_object.address}")
        with grpc.insecure_channel(REGISTRY_ADDRESS) as channel:
            registry_stub = non_blocking_sys_pb2_grpc.RegistryServiceStub(channel)
            registration_response = server_object.register_server(registry_stub)
            if(registration_response.status == "SUCCESS"):
                grpc_server = grpc.server(futures.ThreadPoolExecutor())
                non_blocking_sys_pb2_grpc.add_ServerServiceServicer_to_server(server_object, grpc_server)
                grpc_server.add_insecure_port(server_object.address)
                print(f"\n\n-------- Starting server : {server_object.address} --------\n")
                grpc_server.start()
                grpc_server.wait_for_termination()
            else:
                print(f" -------- Failed to start server : {server_object.address} --------")