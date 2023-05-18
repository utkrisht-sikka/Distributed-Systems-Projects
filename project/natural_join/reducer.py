import time
import grpc
# import readwrite_sys_pb2
# import readwrite_sys_pb2_grpc
import worker_register_pb2
import worker_register_pb2_grpc
import os
from concurrent import futures
from threading import Thread, Lock
from datetime import date
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
from enum import Enum
import random
MASTER_ADDRESS = "localhost:5555";

class Reducer(worker_register_pb2_grpc.ReducerServiceServicer):
    def add_reducer(self):
        add_reducer_response = "None";
        try:
            with grpc.insecure_channel(MASTER_ADDRESS) as channel:
                master_server_stub = worker_register_pb2_grpc.MasterServiceStub(channel)
                add_reducer_request = worker_register_pb2.AddReducerRequest();
                add_reducer_request.ip,add_reducer_request.port = self.address.split(":");
                add_reducer_response = master_server_stub.addReducer(add_reducer_request);
                print("Response received in addServer response={} for address={}".format(add_reducer_response,self.address));

        except Exception as exp:
            print("error occured in addServer method address={} exception={}".format(self.address,exp));
        return add_reducer_response;
    def __init__(self,ip,port,folder_name,intermediate_file_paths,M,R) -> None:
        self.ip = ip;
        self.port = port;
        current_directory = os.path.abspath('./');
        self.M = M;
        self.R = R;
        self.address = ip+":"+str(port);
        self.input_file_paths = intermediate_file_paths;
        self.reducer_name = folder_name;
        self.folder_name = os.path.join(current_directory,folder_name);
        data_path = self.folder_name;

        if not os.path.exists(data_path):
            try:
                os.mkdir(data_path)
            except Exception as exp:
                print("Exception occured while creating directory={} exp={}",data_path,exp);
        else:
            raise BaseException(f"Directory already exists for server={data_path}");
        pass
        # self.add_reducer();
        # result = self.startComputation();
    def generateReducingOutput(self,inp_list):
        reducer_num = self.reducer_name[1:];
        partition = "P"+reducer_num
        final_arr=[]
        cc = 0;
        for file_path in inp_list:
            with open(file_path,"r") as file:
                content = file.read();
                temp_val = content.split("\n");

                temp_val = [x for x in temp_val if x.strip()!=""];
                for item_pres in temp_val:
                    final_arr.append(item_pres);
        output_file = os.path.join(self.folder_name,"output_file.txt");
        if(len(final_arr) == 0):
            with open(output_file,"w") as file:
                file.write("Name, Age, Role\n")
                empty_file=0; 
                          
        final_arr = [x.split(", ") for x in final_arr];
        final_arr = sorted(final_arr,key = lambda x:x[0]);
        
        with open(output_file,"w") as file:
            file.write("Name, Age, Role\n")
            i = 0;
            while i<len(final_arr):
                ind = i;
                while ind<len(final_arr):
                    if(final_arr[i][0]==final_arr[ind][0]):
                        ind+=1;
                    else:
                        break;
                same_key_vals = final_arr[i:ind];
                same_key_vals = sorted(same_key_vals,key = lambda x:x[1]);
                new_ind = -1;
                index= 0;
                for temp in same_key_vals:
                    if temp[1] == "table2":
                        new_ind = index;
                        break;
                    index+=1;
                if(new_ind ==0 or new_ind == -1):
                    print(f"\n In Reducer No join exists for name={final_arr[i][0]} \n");
                else:
                    cc = 1;
                    arr1 = same_key_vals[:index];
                    arr2 = same_key_vals[index:];
                    for first_val in arr1:
                        for second_val in arr2:
                            file.write(first_val[0]+", "+first_val[2]+", "+second_val[2]+"\n");


            
                i = ind;
        return output_file;


                    



    def startComputation(self, request, context):
        time.sleep(4);
        general_message =  worker_register_pb2.GeneralMessageResponse();
        # try:
        address = self.address;
        main_files = request.message_val;
        inp_list = main_files.strip().split(" ");
        output_file_path = self.generateReducingOutput(inp_list);
        general_message.message_val = output_file_path;


        # except Exception as arg:
        #     print(f"exception occured in startComputation method={arg}")
        return general_message;
    def checkFunctionality(self,main_files):
        inp_list = main_files.strip().split(" ");
        output_file_path = self.generateReducingOutput(inp_list);
        print(output_file_path);
def main(ip,port,folder_name,intermediate_file_paths,M,R,timeout):
    reducer_object = Reducer(ip,port,folder_name,intermediate_file_paths,M,R);
    if(reducer_object.address == "localhost:5555"):
        print("Cannot take the address of Master")
    
    else:
        print(f"\n---> DEPLOYING REDUCER {reducer_object.address} ----< \n")
        
        print(f"Registering REDUCER_{reducer_object.reducer_name} {reducer_object.address}")
        registration_response = reducer_object.add_reducer();
        print(f"response after registration={registration_response}");
        
        # if(registration_response.status.find("SUCCESS")!=-1):
            # resulting_response = mapper_object.startComputation();
        grpc_server = grpc.server(futures.ThreadPoolExecutor())
        worker_register_pb2_grpc.add_ReducerServiceServicer_to_server(reducer_object, grpc_server)
        grpc_server.add_insecure_port(reducer_object.address)
        print(f"\n\n-------- Starting REDUCER : {reducer_object.address} --------\n")
        grpc_server.start()

        if(timeout != 0):
            grpc_server.wait_for_termination(timeout)
        else:
            grpc_server.wait_for_termination()
# if __name__=="__main__":
#     print(33);
#     path1_new = os.path.abspath("./");
    
#     path1 = path1_new;
#     new_path = os.path.join(path1,"M0","P1.txt");
#     new_path2 = os.path.join(path1,"M1","P1.txt");
#     new_path3 = os.path.join(path1,"M2","P1.txt");
#     new_str = new_path+" "+new_path2+" "+new_path3;
#     input_file_paths = new_str;
#     print(input_file_paths);
#     ip,port,folder_name,M,K = "localhost",5556,"R0",3,2;
#     mapper_obj = Reducer(ip,port,folder_name,input_file_paths,M,K);
#     mapper_obj.checkFunctionality(input_file_paths);
