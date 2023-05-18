import shutil
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
from multiprocessing import Process
import mapper
import reducer
MASTER_ADDRESS = "localhost:5555";
temp = 0;
response_arr2=[]
def new_method(inp_val,address_val,response_arr):
    # time.sleep(9);
    final_response = "None";
    computing_input = worker_register_pb2.GeneralRequest();
    computing_input.message_val = inp_val;
    with grpc.insecure_channel(address_val) as main_channel:
        mapper_stub = worker_register_pb2_grpc.MapperServiceStub(main_channel);
        # computing_input= worker_register_pb2.GeneralRequest();
        # computing_input.message_val = ' '.join(inp_list[i]);
        final_response = mapper_stub.startComputation(computing_input);
    # return final_response;
def new_method_red(inp_val,address_val,output_dir,red_val):
    computing_input = worker_register_pb2.GeneralRequest();
    computing_input.message_val = inp_val;
    
    with grpc.insecure_channel(address_val) as main_channel:
        reducer_stub = worker_register_pb2_grpc.ReducerServiceStub(main_channel);
        
        final_response = reducer_stub.startComputation(computing_input);
    content = "None";
    with open(final_response.message_val,"r") as kk:
        content = kk.read();
    red = str(red_val);
    with open(os.path.join(output_dir,red+"_output_file.txt"),"w") as file:
        file.write(content);
        # response_arr.append(final_response.message_val);

class Master(worker_register_pb2_grpc.MasterServiceServicer):
    def removePreviousStaleDirectories(self):
        try:
            current_directory = os.path.abspath('./');
            data_directory1 = "M";
            data_directory2 = "R";
            file_list = os.listdir(current_directory)
            for file_loc in file_list:
                if(os.path.isdir(os.path.join(current_directory,file_loc))):
                    if(file_loc.find(data_directory1)!=-1 or file_loc.find(data_directory2)!=-1):
                        shutil.rmtree(os.path.join(current_directory,file_loc));
            new_file_list = os.listdir(current_directory)
            
            
        except Exception as arg:
            print("error occured in removing previous directories exception={}".format(arg));
    def create_directory(self):
        current_directory = os.path.dirname(os.path.abspath('./'));
        data_directory = self.folder_name;
        data_path = os.path.join(current_directory,data_directory);
        self.folder_name = data_path;
        # folder_name -> input_folder_name;
        return data_path;
    

    def __init__(self, folder_name,output_folder,M,R):
        self.removePreviousStaleDirectories();
        self.address = MASTER_ADDRESS;
        self.M = M;
        self.R = R;
        self.folder_name = folder_name
        self.output_folder = output_folder
        self.lock = Lock()
        self.mapper_list=[];
        self.reducer_list=[];
        self.response_arr=[]
        self.mapper_set=set();
        self.reducer_set=set();
        self.create_directory();
        # self.startWork();
    def addMapper(self, request, context):
        general_response = worker_register_pb2.GeneralResponse();
        address=None;
        try:
            ip = request.ip;
            port = request.port;
            address = ip+":"+str(port);
            if( address not in self.mapper_set):
                self.mapper_set.add(address);
                self.mapper_list.append(address);
                general_response.status = "SUCCESS";
            else:
                general_response.status = "FAILURE, The Mapper is already registered";

        except Exception as arg:
            print(f"Exception occured in addMapper with address={address}");
            general_response.status = "FAILURE";
        return general_response;
    
    def addReducer(self, request, context):
        general_response = worker_register_pb2.GeneralResponse();
        address=None;
        try:
            ip = request.ip;
            port = request.port;
            address = ip+":"+str(port);
            if( address not in self.reducer_set):
                self.reducer_set.add(address);
                self.reducer_list.append(address);
                general_response.status = "SUCCESS";
            else:
                general_response.status = "FAILURE, The Mapper is already registered";

        except Exception as arg:
            print(f"Exception occured in addMapper with address={address}");
            general_response.status = "FAILURE";
        return general_response;

    def startMapperComputation(self,inp_list):
        '''
        request_input = readwrite_sys_pb2.Empty();
        write_servers_list = stub.getWriteServers(request_input);
        resulting_list=[]
        '''
        time.sleep(2);
        print("Map Task Asignment Strategy : \n");
        # start_time = time.time()
        
        M = self.M;
        addresses = ["localhost:"+str(5556+i) for i in range(M)];
        response_arr=[]
        prs=[]
        global response_arr2;
        for i in range(M):
            address_val = addresses[i];
            computing_input= worker_register_pb2.GeneralRequest();
            computing_input.message_val = ' '.join(inp_list[i]);
            display_msg = ', '.join(inp_list[i]);
            print(f"\nMAPPER_{i} address={address_val} assigned_splits={display_msg}\n")
            tk = Process(target=new_method,args=(computing_input.message_val,address_val,response_arr));
            # tk.start();
            prs.append(tk);
            # response_arr.append(final_response);
            # print(f"address_val here is={address_val}");
            # with grpc.insecure_channel(address_val) as main_channel:
            #     mapper_stub = worker_register_pb2_grpc.MapperServiceStub(main_channel);
            #     computing_input= worker_register_pb2.GeneralRequest();
            #     computing_input.message_val = ' '.join(inp_list[i]);
            #     print(f"message_val for startComputation={computing_input.message_val}")
            #     final_response = mapper_stub.startComputation(computing_input);
            #     response_arr.append(final_response.message_val);
        for j in prs:
            j.start();
        main_path = os.path.abspath("./");
        cc = 0;
        while(True):
            list_dir_vals = [len(os.listdir(os.path.join(main_path,"M"+str(i)))) if os.path.isdir(os.path.join(main_path,"M"+str(i))) else 0 for i in range(M)];
            min_val = min(list_dir_vals);
            # print(f"min_val={min_val}");
            # print(len(response_arr2));
            if(min_val>0 or cc>2):
                break;
            else:
                
                cc+=1;time.sleep(0.2);
                continue;
            
        # end_time = time.time()

        # elapsed_time = end_time - start_time

        # # print the elapsed time
        # print(f"Elapsed time: {elapsed_time:.4f} seconds")
        # response_arr2=[]
        for j in prs:
            j.join();

        response_arr = ["None"]*M;
        for i in range(M):
            response_arr[i] = os.path.join(main_path,"M"+str(i));
        time.sleep(2);
        print("\nIntermediate Files\n");
        for i in range(M):
            file_name = os.listdir(os.path.join(os.path.abspath("./"),"M"+str(i)))
            print(f"\n MAPPER_{i} address={addresses[i]}");
            if(len(file_name)==0): response_arr[i] = "None";
            for temp in file_name:

                print(os.path.join(os.path.abspath("./"),"M"+str(i),temp));
            print("\n")
        # for i in range(M):
        #     with open(response_arr[i],"r") as file:
        #         temp = file.read();
        #         temp = temp.split("\n");
        #         print(temp);
        #         for kk in temp:
        #             print("kk=",kk);
        print("Mapper phase finished in startMapperComputation");
        return response_arr;
    def startReducerComputation(self,response_arr):
        print("\nReducer Task Asignment Strategy : \n");
        file_locs=[[] for i in range(self.R)];
        for i in range(self.R):
            reducer_num = str(i);
            for temp in response_arr:
                new_path = os.path.join(temp,"P"+reducer_num+".txt");
                file_locs[i].append(new_path);
        final_str = [' '.join(file_locs[i]) for i in range(len(file_locs))];
        display_str = [', '.join(file_locs[i]) for i in range(len(file_locs))]
        addresses = ["localhost:"+str(5556+i+self.M) for i in range(self.R)];
        response_arr=["None"]*R;
        prs=[]
        for i in range(self.R):
            address_val = addresses[i];
            computing_input= worker_register_pb2.GeneralRequest();
            computing_input.message_val = final_str[i];
            print(f"\n Reducer_{i} address={address_val} assigned_partition_files={display_str[i]}")
            tk = Process(target=new_method_red,args=(computing_input.message_val,address_val,self.output_folder,"R"+str(i)));
            # tk.start();
            prs.append(tk);
            # print(f"address_val here is={address_val}");
        for j in prs:
            j.start();
        response_arr = ["None"]*R;
        main_path = os.path.abspath("./");
        for i in range(R):
            response_arr[i] = os.path.join(main_path,"R"+str(i),"output_file.txt")
        
        # while(True):
        #     list_dir_vals = [len(os.listdir(os.path.join(main_path,"R"+str(i)))) if os.path.isdir(os.path.join(main_path,"R"+str(i))) else 0 for i in range(M)];
        #     min_val = min(list_dir_vals);
        #     # print(len(response_arr2));
        #     if(min_val==1):

        #         break;
        #     else:
        #         continue;
        time.sleep(2);
        print("\nOutput Files\n");
        for i in range(self.R):
            print(f" \n REDUCER_{i} address={addresses[i]} output_file={response_arr[i]} \n")



        for j in prs:
            j.join();
        print("Computation finished for all reducers");
        return response_arr;



                    



# def main(M_val,R_val,folder_name,timeout):
#     # M_val = int(input("PLease enter the value of M:"))
#     # R_val = int(input("PLease enter the value of R:"))
#     # M_val = 2;R_val = 2;
#     master_object = Master(folder_name=os.path.join("Sample_Files","natural_join","input"),M=M_val,R=R_val);
#     print("master server address={}".format(MASTER_ADDRESS));
#     # try:
#     with grpc.insecure_channel(MASTER_ADDRESS) as channel:
#         grpc_server = grpc.server(futures.ThreadPoolExecutor())
#         worker_register_pb2_grpc.add_MasterServiceServicer_to_server(master_object, grpc_server)
#         grpc_server.add_insecure_port(master_object.address);
#         print(f"\n\n-------- Starting Master : {master_object.address} --------\n")
#         grpc_server.start()
#         grpc_server.wait_for_termination()
#         print(23);
#         master_object.startWork();
         


        

if __name__=="__main__":
        # first spawn M mappers by creating a script.
        #after that spawn R reducers
        #Now start work.
    start_time = time.time();
    # M = int(input("Please enter the value of M:"));
    # R = int(input("Please enter the value of R:"));
    mappers=[]
    path_name = os.path.abspath('./');
    final_name = os.path.dirname(path_name);
    
    input_folder = input("Please enter the folder directory that has the input: ");
    output_dir = input("Please enter the output directory : ");
    # temp_folder_name = os.path.join("Sample_Files","natural_join","input");
    folder_path = input_folder;
    input_path = os.listdir(input_folder);
    
    for temp in input_path:
        if(temp.find("config.txt")!=-1):
            path_val = os.path.join(folder_path,temp);
            with open(path_val,"r") as file:
                content = file.read();
                temp_list = content.split("\n");
                M = int(temp_list[0].split(" ")[2]);
                R = int(temp_list[1].split(" ")[2]);

    # master_start = Master(os.path.join(final_name,temp_folder_name),M,R);
    master_start = Master(input_folder,output_dir,M,R);

    grpc_master = grpc.server(futures.ThreadPoolExecutor())
    worker_register_pb2_grpc.add_MasterServiceServicer_to_server(master_start, grpc_master)
    grpc_master.add_insecure_port(master_start.address)
    print(f" ------------ Starting Master at {master_start.address}--------------------")
    print(f"master_obj address={master_start.address} M={master_start.M} R={master_start.R} input_data_loc={input_folder}\n\n")
    print(master_start)
    # print("\n\n")
    
    grpc_master.start()
    # time.sleep(1);
    
    list_dir = os.listdir(input_folder);
    final_path_list=[]
    for temp in list_dir:
        if(temp.find("config")==-1):
            final_path_list.append(os.path.join(input_folder,temp));
    inp_list = [[] for i in range(M)];
    for k in range(len(final_path_list)):
        ind_val = k%M;
        inp_list[ind_val].append(final_path_list[k]);
    # master_ser = Process(target = main,args=())
    for i in range(M):
        abc = inp_list[i];
        xyz = ' '.join(abc);
        mappers.append(Process(target = mapper.main, args=("localhost",5556+i,"M"+str(i),xyz,M,R,50,)))
        
        
    for i in mappers:
        i.start()
        time.sleep(2);
        # time.sleep(1)
    
    
    output_arr_mapper = master_start.startMapperComputation(inp_list);
    print("--------------------------------------------------c------------------------------------------------------")
    
    filtered_output=[]
    for temp in output_arr_mapper:
        if(temp!="None"):
            filtered_output.append(temp);
    output_arr_mapper = filtered_output;

    reducers=[];
    for i in range(R):
        abc = [os.path.join(x,"P"+str(i)) for x in output_arr_mapper];
        xyz = ' '.join(abc);
        reducers.append(Process(target = reducer.main, args=("localhost",5556+i+M,"R"+str(i),xyz,M,R,50,)))
    for i in reducers:
        i.start();
        time.sleep(2);
        # time.sleep(1);
    # for i in mappers:
    #     i.join()
    final_output_arr = master_start.startReducerComputation(output_arr_mapper);
    
    for temp in final_output_arr:
        content_val = "";
        file_new = open(temp,"r");
        content_val = file_new.read();
        file_new.close();
        ind = temp.rfind("R");
        ind_new = temp.rfind("\o");
        red = temp[ind:ind_new];
        with open(os.path.join(output_dir,red+"_output_file.txt"),"w") as file:
            file.write(content_val);
        

    print("Computation finished for Reducers")
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Total Elapsed time for whole process: {elapsed_time:.4f} seconds")
    # grpc_master.wait_for_termination()
    for i in mappers:
        i.join();
    for i in reducers:
        i.join();
    exit();
    
    pass;





    
    
                
 