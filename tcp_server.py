# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:28:09 2021

@author: DELL
"""
import tkinter as tk
from tkinter import ttk
import math
import socket
import time
import threading

'''
1. The server starts and waits for filename.
2. The client sends a filename.
3. The server receives filename.
   If file is present,
   server starts reading file 
   and continues to send a buffer filled with
   file contents encrypted until file-end is reached.
4. End is marked by EOF.
5. File is received as buffers until EOF is 
received. Then it is decrypted.
6. If Not present, a file not found is sent.

Encryption: XOR Encryption
'''
# SERVER TCP : WITH XOR ENCRYPTION

def encrypt(msg): 
    # encrypt / decrypt
    xorKey='P'
    encrypted = ''
    for i in range(0,len(msg)):
        encrypted=encrypted+chr(ord(msg[i])^ ord(xorKey))
    return encrypted

def send():
    global pb,t1
    try:
        if t1.is_alive():
            t1.kill()
    except NameError:
        t1=myThread()
        t1.start()
        time.sleep(0.01)
    finally:
        clear()

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 
    def run(self):
        boolean=False
        try:
            self.connect_server()
            boolean=self.open_file(self.file_name)
        except ConnectionAbortedError:
            t2=updatorThread('Status of request\n Client '+str(self.addr)+': Unsuccessful')
            t2.start()
            return
        except OSError:
            t2=updatorThread('OS Error: Restart Server')
            t2.start()
            return
        except ConnectionResetError:
            t2=updatorThread('ConnectionResetError:\n Client'+str(self.addr)+' closed connection forcibly')
            t2.start()
            return
        except RuntimeError:
            t2=updatorThread('RuntimeError')
            t2.start()
            return
        try:
            if boolean:
                self.send_file(self.file_name)
        except ConnectionResetError:
            pb.destroy()
            t2=updatorThread('Status of request\n Client '+str(self.addr)+': Unsuccessful')
            t2.start()
            return
        
    def connect_server(self):
        HOST = 'localhost'
        PORT = 50007
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        t2=updatorThread('Server Listening')
        t2.start()
        
        self.conn, self.addr = self.s.accept()
        t2=updatorThread('Connected by '+str(self.addr))
        t2.start()
        
        file_name = self.conn.recv(4096)
        self.file_name= file_name.decode(encoding="utf-8")
        t2=updatorThread('File name: '+self.file_name)
        t2.start()
        print()
    def open_file(self,file_name):
        try:
            self.fo = open(file_name, "rb")
            self.data = self.fo.read()
            self.fo.close()
            t2=updatorThread('File read')
            t2.start()
            print('File read')
            return True
        except Exception:
            t2=updatorThread('File not found')
            t2.start()
            print('File not found')
            self.conn.send('File not found'.encode(encoding="utf-8"))
            self.conn.close()
            return False
    def send_file(self,file_name):
        global pb
        buffer_size=10000
        packet_no=1
        data_length=len(self.data)
        total_packets = math.ceil(data_length/buffer_size)
        print("total packets:",total_packets)
        t2=updatorThread('File Size:  '+str(data_length)+'bytes')
        t2.start()
        print('File Size:  '+str(data_length)+'bytes')
        
        self.conn.send(str(total_packets).encode(encoding="utf-8"))
        time.sleep(0.5)
        self.conn.send(str(buffer_size).encode(encoding="utf-8"))
        
        t2=updatorThread('Progress: 0 %')
        t2.start()
        
        pb=ttk.Progressbar(root,orient='horizontal',mode='determinate',length=200)
        canvas1.create_window(150,250,window=pb)
        time.sleep(2)
        
        self.fo = open(self.file_name, "rb")
        while (packet_no<=total_packets):
            s1=self.fo.read(buffer_size)
            self.conn.send(s1)
            time.sleep(1)
            packet_no+=1
            progress=packet_no/total_packets*100
            t2=updatorThread('Progress %3.2f %%' %(progress))
            t2.start()
            pb['value']=progress
        if(self.conn!=-1):
            print('\nData Sent to Client '+str(self.addr)+': Successful')
            t2=updatorThread('Data Sent to Client '+str(self.addr)+': Successful')
            t2.start()
            self.conn.close()
            pb.destroy()
        self.conn.close()
        self.s.close()
        self.fo.close()
        

class updatorThread(threading.Thread):
    def __init__(self,msg):
        threading.Thread.__init__(self)
        self.msg=msg
    def run(self):
        self.update_status()
    def update_status(self):
        global label1
        label1.config(text=self.msg)
        time.sleep(1)

def clear():
    global label1,pb,t1
    try:
        if not t1.is_alive():
            pb.destroy()
    except:
        time.sleep(0.01)
    label1.config(text='')
    entry1.delete(0, 15)

if __name__ == "__main__":
    root = tk.Tk()
    root.title('TCP File Transfer')

    canvas1 = tk.Canvas(root, width=300, height=300)
    canvas1.pack()
    
    global label1, file_name, data, entry1, pb
    entry1 = tk.Entry(root)
    canvas1.create_window(150, 120, window=entry1)

    button1 = tk.Button(text='Listen', command=send)
    
    canvas1.create_window(120, 170, window=button1)

    button2 = tk.Button(text='Clear', command=clear)
    canvas1.create_window(190, 170, window=button2)

    label1 = tk.Label(root, text="")
    canvas1.create_window(150, 220, window=label1)
    root.mainloop()
