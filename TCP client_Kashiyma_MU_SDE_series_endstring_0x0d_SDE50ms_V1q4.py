# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 14:17:30 2023

@author: USER11
"""

import socket
import sys
import time
import select



def main():
    ###---MU series requset command ---
    DP_MotorCurrent='40303052453030343534323030303135312A0D'
    DP_CaseTemperature='40303052453030343534333030303135302A0D'
    DP_CoolingWater='40303052453030343534343030303135372A0D'
    DP_N2PurgeFlow='40303052453030343534363030303135352A0D'
    MB_MotorCurrent='40303052453030343535303030303135322A0D'
    DP_MotorSpeed='40303052453030343535323030303135302A0D'
    MB_MotorSpeed='40303052453030343535333030303135312A0D'

    MU_CMD=[
            DP_MotorCurrent, 
            DP_CaseTemperature,
            DP_CoolingWater,
            DP_N2PurgeFlow,
            MB_MotorCurrent,
            DP_MotorSpeed,
            MB_MotorSpeed        
            ]
    ###---SDE series requset command ---
    SDE_AnalogData='024134332A0D'
     
    
    SDE_CMD=[
            SDE_AnalogData     
            ]
 
    Pump_Series=''
    recv_buffer_size=255
    recv_hex_data=b''
    # MU_An_Data = np.zeros((len(MU_CMD),1) ,dtype=float)
    MU_An_Data =[0.]*len(MU_CMD)
    #SDE_An_Data = np.zeros((6,1) ,dtype=float)
    SDE_An_Data =[0.]*6 # #SDE603X-136 series valid parameters :6
    try:
        ###connection setting
        #host = input("Enter IP address: ")
        #port = int(input("Enter PORT: "))
        host = "192.168.1.40"
        port = 1001
        
        ###pump series entry
        while True:
            Pump_Series=input("Enter Pump Series(MU or SDE): ")
            if Pump_Series =="MU" or Pump_Series =="SDE":
                break 
            else:               
                print("Pump series is not correct!")
            
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #---Keep connection alive setting---
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)#socket option turn on keep alive
        after_idle_msec=60000
        interval_msec=30000
        client_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (True, after_idle_msec, interval_msec))#socket option turn on keep alive
        #-----------------------------
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}, Kashiyama {Pump_Series} Series")
        
        if Pump_Series =="MU":    
            while True:
                MU_CMDbytes={}
                for i in range(len(MU_CMD)):
                    ###send command
                    MU_CMDbytes[i]=bytes.fromhex(MU_CMD[i])
                    print(f"Send : {MU_CMDbytes[i]}")
                    print(f"send(hex) : {MU_CMD[i]}")
                    #print(MU_CMDbytes[i][7:11])#test
                    client_socket.sendall(MU_CMDbytes[i])
                    time.sleep(0.1)
                    ###receviced response
                    ready, _, _ = select.select([client_socket], [], [], 0.15)  # 等待 150 毫秒
                    if ready:
                        data = client_socket.recv(recv_buffer_size)
                        if not data:  # 如果接收到的資料是空的，表示連線已經關閉，可以在這裡進行相應處理
                            break
                        recv_hex_data += data
                        while b'\x0d' in recv_hex_data:
                            idx = recv_hex_data.find(b'\x0d')
                            received_data = recv_hex_data[:idx+1]
                            recv_hex_data = recv_hex_data[idx + 1:]                        
                            #hex_string = received_data.hex().upper()
                            #print(f"Received: {hex_string}"
                            ###get analog data
                            MU_An_Data[i] = int(received_data[7:11])  
                         
                            # hex_string=Read_MU_data.hex().upper()
                            print(f"Received: {received_data}")
                            print(f"Received(hex): {received_data.hex().upper()}")
                            # print(received_data.hex().upper())
                    time.sleep(0.1)
                print("---Kashiyama MU series Analog Data---")    
                print(f"DP Motor Current : {MU_An_Data[0]/10} A")
                print(f"DP Case Temperature : {MU_An_Data[1]} °C")
                print(f"DP Cooling Water : {MU_An_Data[2]/10} L/min")
                print(f"DP N2 Purge Flow : {MU_An_Data[3]/10} SLM")
                print(f"MB Motor Current : {MU_An_Data[4]/10} A")
                print(f"DP Motor Speed : {MU_An_Data[5]} rpm")
                print(f"MB Motor Speed : {MU_An_Data[6]} rpm")
            time.sleep(1)
                
                
                
        if Pump_Series =="SDE": 
            #print("SDE no program!")
            while True:
                SDE_CMDbytes={}
                for i in range(len(SDE_CMD)):
                    ###send command
                    SDE_CMDbytes[i]=bytes.fromhex(SDE_CMD[i])
                    print(f"Send : {SDE_CMDbytes[i]}")
                    print(f"send(hex) : {SDE_CMD[i]}")
                    #print(MU_CMDbytes[i][7:11])#test
                    client_socket.sendall(SDE_CMDbytes[i])
                    time.sleep(0.05)
                    ###receviced response
                    ready, _, _ = select.select([client_socket], [], [], 0.500)  # 等待 500 毫秒
                    if ready:
                        data = client_socket.recv(recv_buffer_size)
                        if not data:  # 如果接收到的資料是空的，表示連線已經關閉，可以在這裡進行相應處理
                            break
                        recv_hex_data += data
                        while b'\x0d' in recv_hex_data:
                            idx = recv_hex_data.find(b'\x0d')
                            received_data = recv_hex_data[:idx+1]
                            recv_hex_data = recv_hex_data[idx + 1:]                        
                            #hex_string = received_data.hex().upper()
                            #print(f"Received: {hex_string}"
                            ###get analog data                           
                            #SDE603X-136 series valid parameters :
                            SDE_An_Data[0] = int(received_data[3:6])    #DP Motor current
                            SDE_An_Data[1] = int(received_data[6:9])    #MBP Motor current  
                            SDE_An_Data[2] = int(received_data[9:12])   #DP Case Temperature  
                            SDE_An_Data[3] = int(received_data[21:24])  #DP Back Pressure   
                            SDE_An_Data[4] = int(received_data[24:27])  #DP Cooling water  
                            SDE_An_Data[5] = int(received_data[30:33])  #N2 Purge       
    
                            # hex_string=Read_MU_data.hex().upper()
                            print(f"Received: {received_data}")
                            print(f"Received(hex): {received_data.hex().upper()}")
                            # print(received_data.hex().upper())
                    #time.sleep(0.05)
                print("---Kashiyama SDE603X-136 Analog Data---")    
                print(f"DP Motor Current : {SDE_An_Data[0]/10} A")
                print(f"MBP Motor Current : {SDE_An_Data[1]/10} A")
                print(f"DP Case Temperature : {SDE_An_Data[2]} °C")
                print(f"DP Back Pressure : {SDE_An_Data[3]} k Pa")
                print(f"DP Cooling Water : {SDE_An_Data[4]/10} L/min")
                print(f"DP N2 Purge Flow : {SDE_An_Data[5]/10} SLM")
                time.sleep(1)
 

        
    except KeyboardInterrupt:
        print("Exit program")
        sys.exit()
    except socket.error as e:
       if e.errno == 10054:  # WinError 10054
           print("Connection refused by the remote computer.")           
           sys.exit()
    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()# -*- coding: utf-8 -*-

           