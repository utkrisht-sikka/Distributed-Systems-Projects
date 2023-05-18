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
import numpy as np
import pandas as pd
from copy import deepcopy
# from master import MASTER_ADDRESS
MASTER_ADDRESS = "localhost:5555";

class Mapper(worker_register_pb2_grpc.MapperServiceServicer):
    def add_mapper(self):
        add_mapper_response = "None";
        try:
            with grpc.insecure_channel(MASTER_ADDRESS) as channel:
                master_server_stub = worker_register_pb2_grpc.MasterServiceStub(channel)
                add_mapper_request = worker_register_pb2.AddMapperRequest();
                add_mapper_request.ip,add_mapper_request.port = self.address.split(":");
                add_mapper_response = master_server_stub.addMapper(add_mapper_request);
                print("Response received in addMapper response={} for address={}".format(add_mapper_response,self.address));

        except Exception as exp:
            print("error occured in addMapper method address={} exception={}".format(self.address,exp));
        print("add_server_response={}".format(add_mapper_response));
        return add_mapper_response;

    def generateMappingOutput(self,input_list):
        my_dir = self.folder_name;
        stage1_output=[]
        for file_name in input_list:
            
            f = open(os.path.join(self.input_file_paths, file_name), "r");
            content = f.read();
            f.close();
            split_by_line = content.strip().split("\n");
            temp = [x.split(", ") for x in split_by_line];
            if(len(temp)==0 or type(temp[0])!=type([2]) or len(temp[0])!=2):
                temp = [x.split(",") for x in split_by_line];
            # if((file_name.lower().find("table1")!=-1 and self.ind1 ==1)
            #     or (file_name.lower().find("table2")!=-1 and self.ind2 ==1)):
            #     new_temp = deepcopy(temp);
            #     for xa in range(len(new_temp)):
            #         new_temp[xa][0],new_temp[xa][1] = new_temp[xa][1],new_temp[xa][0];
            #     temp = deepcopy(new_temp);
            for (xa,ya) in enumerate(temp):
                name_col = ya[0];
                other_col = ya[1];
                if(xa==0):
                    # print(name_col,other_col)
                    # stage1_output.append([name_col,["Table_Name",other_col]])
                    # print()
                    continue;
                if(file_name.lower().find("table1")!=-1):
                    new_str = "table1, "+other_col;
                    stage1_output.append([name_col,["table1",other_col]])

                elif(file_name.lower().find("table2")!=-1):
                    new_str = "table2, "+other_col;
                    stage1_output.append([name_col,["table2",other_col]])

                
                    # Generate fake exception

            # stage 2 work of mapper
        if_file_path = os.path.join(self.folder_name,"if_file.txt");
        with open(if_file_path,"w") as file:
            for temp_val in stage1_output:
                xa,ya = temp_val;
                file.write(xa+", "+ya[0]+", "+ya[1]+"\n");
        partition_dict = {};
        for i in range(self.R):
            partition_dict["P"+str(i)] = [];
        
        r_val = self.R;
        for (xa,ya) in enumerate(stage1_output[0:]):
            key_val = ya[0];
            partition = "P"+str(len(key_val)%r_val);
            if(partition in partition_dict):
                partition_dict[partition].append(ya);
            else:
                partition_dict[partition] = [ya];

        
    
        for key_name in partition_dict:
            partition_file_path = os.path.join(my_dir,key_name+".txt");
            with open(partition_file_path, "w") as file:
                # file.write(stage1_output[0][0]+" "+stage1_output[0][1]+" "+stage1_output[0][2]+"\n");
                for temp_val in partition_dict[key_name]:
                    key_name = temp_val[0];
                    table_name = temp_val[1][0];
                    val_name = temp_val[1][1];
                    file.write(key_name+", "+table_name+", "+val_name+"\n");
        
        return self.folder_name;
    
    def startComputation(self, request, context):
        # print('before sleep')
        time.sleep(4)
        # print('after sleep')
        general_message =  worker_register_pb2.GeneralMessageResponse();
        # try:
        address = self.address;
        main_files = request.message_val;
        
        # print(f"all_files location received={main_files}");
        if(main_files.strip()==""):
            general_message.message_val = "None";
            return general_message;
        inp_list = main_files.strip().split(" ")
        for x in inp_list:
            if(x.find("config")!=-1):
                main_files.remove(x);
                break;
        output_file_path = self.generateMappingOutput(inp_list);
        general_message.message_val = output_file_path;
        # print(f"output_file returned by mapper={self.folder_name} to master has path={output_file_path}")


        # except Exception as arg:
        #     print(f"exception occured in startComputation method={arg}")
        return general_message;
    def checkFunctionality(self):
        inp_list = self.input_file_paths.strip().split(" ")
        output_file_path = self.generateMappingOutput(inp_list);
        # general_message.message_val = output_file_path;
        # print(f"output_file returned by mapper={self.folder_name} to master has path={output_file_path}")


    def __init__(self,ip,port,folder_name,input_file_paths,M,R) -> None:
        self.ip = ip;
        self.port = port;
        current_directory = os.path.abspath('./');
        self.M = M;
        self.R = R;
        
        self.address = ip+":"+str(port);
        self.input_file_paths = input_file_paths;
        self.mapper_name = folder_name;
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
        # self.add_mapper();
        # result = self.startComputation();
def main(ip,port,folder_name,input_file_paths,M,R,timeout):
    mapper_object = Mapper(ip,port,folder_name,input_file_paths,M,R);
    if(mapper_object.address == "localhost:5555"):
        print("Cannot take the address of Master")
    
    else:
        print(f"\n---> DEPLOYING MAPPER {mapper_object.address}")
        
        print(f"Registering MAPPER_{mapper_object.mapper_name} {mapper_object.address}")
        registration_response = mapper_object.add_mapper();
        print(f"Registration response={registration_response}");
        
        # if(registration_response.status.find("SUCCESS")!=-1):
            # resulting_response = mapper_object.startComputation();
        grpc_server = grpc.server(futures.ThreadPoolExecutor())
        worker_register_pb2_grpc.add_MapperServiceServicer_to_server(mapper_object, grpc_server)
        grpc_server.add_insecure_port(mapper_object.address)
        print(f"\n-------- Starting Mapper : {mapper_object.address} --------\n")
        grpc_server.start()

        if(timeout != 0):
            grpc_server.wait_for_termination(timeout)
        else:
            grpc_server.wait_for_termination()
# if __name__=="__main__":
#     path1_new = os.path.abspath("./");
#     path11_new = os.path.dirname(path1_new);
#     # path1 = "C:\Users\91995\Documents\GitHub\DSCD-Winter-2023\project\Sample_Files";
#     path1 = path11_new;
#     new_path = os.path.join(path1,"Sample_Files","natural_join","input","input1_table1.txt");
#     new_path2 = os.path.join(path1,"Sample_Files","natural_join","input","input2_table1.txt");
#     new_str = new_path+" "+new_path2;
#     input_file_paths = new_str;
#     print(input_file_paths);
#     ip,port,folder_name,M,K = "localhost",5556,"M0",2,2;
#     mapper_obj = Mapper(ip,port,folder_name,input_file_paths,M,K);
#     mapper_obj.checkFunctionality();

        


