# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:49:57 2021

@author: DELL
"""

# CLIENT TCP : WITH XOR ENCRYPTION

import tkinter as tk
from tkinter import ttk
import socket
import time
import threading

def encrypt(msg): 
    # encrypt / decrypt
    xorKey='P'
    encrypted = ''
    for i in range(0,len(msg)):
        encrypted=encrypted+chr(ord(msg[i])^ ord(xorKey))
    return encrypted

def ask():
    global entry1,t1,pb
    try:
        pb['value']=0
    except:
        time.sleep(0.01)
    finally:
        file_name = entry1.get()
        t1=myThread(file_name)
        t1.start()

class myThread(threading.Thread):
    def __init__(self,file_name):
        threading.Thread.__init__(self) 
        self.data=b''
        self.file_name = file_name
    def run(self):
        global pb
        boolean=False
        try:
            boolean=self.connect_server(self.file_name)
        except ConnectionRefusedError:
            t2=updatorThread('Host unavailable')
            t2.start()
        except RuntimeError:
            t2=updatorThread('RuntimeError at Server side')
            t2.start()
        except Exception as e:
            t2=updatorThread('Error!'+e.msg)
            t2.start()
        finally:
            pb.destroy()
        if boolean:
            self.save_to_file()
    def connect_server(self,file_name):
        global pb
        HOST = 'localhost'
        PORT = 50007
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        t2=updatorThread('Connection Established')
        t2.start()
        time.sleep(1)
        
        sock.send(self.file_name.encode(encoding="utf-8"))
        
        data1 = sock.recv(4096)
        total= data1.decode(encoding="utf-8")
        if (total=="File not found"):
            t2=updatorThread('File not found at server')
            t2.start()
            print('File not found at server')
            return False
        total=float(total.strip())
        print('Total packets:',total)
        if(total==0):
            t2=updatorThread('File Empty')
            t2.start()
            print('File Empty')
            return False
        data1 = sock.recv(4096)
        buff_size= data1.decode(encoding="utf-8")
        buff_size=float(buff_size.strip())
        print('Buffer',buff_size)
        t2=updatorThread('File Size: '+str(total*buff_size)+'bytes')
        t2.start()
        print('File size'+str(total*buff_size)+'bytes')
        
        curr_packet=0.0
        message=b''
        progress=0
        count=0
        
        pb=ttk.Progressbar(root,orient='horizontal',mode='determinate',length=200)
        canvas1.create_window(150,250,window=pb)
        
        while(curr_packet<total):
            data_encoded = sock.recv(int(buff_size))
            if data_encoded:
                data_string = data_encoded
                if len(data_string)==0:
                    count+=1
                if count==3:
                    raise RuntimeError
                progress=curr_packet/total*100
                t2=updatorThread('Progress: %3.2f %%' %(progress))
                t2.start()
                pb['value']=progress
                message=message+data_string
                curr_packet+=1
        self.data=message
        t2=updatorThread('File Recieved from server: Successfully')
        t2.start()
        print('Entire Data received from server: Successful\n')
        return True
    
    def save_to_file(self):
        global button1,file_data,event_object,entry1,pb
        button1['text']='Save here'
        button1.configure(command=save)
        try:
            pb.destroy()
        except:
            time.sleep(0.01)
        event_object.wait()
        file_name = entry1.get()
        fo=open(file_name,"wb")
        fo.write(self.data)
        fo.close()

def save():
    try:
        global event_object,button1
        event_object.set()
        t2=updatorThread('Saved to file.')
        t2.start()
        button1['text']='Ask for file'
        button1.configure(command=ask)
    except Exception as e:
        print('Error Message: ',e.msg)

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
    label1.config(text='')
    entry1.delete(0, 15)
    if not t1.isAlive():
        try:
            pb.destroy()
        except:
            time.sleep(0.01)


if __name__ == "__main__":
    root = tk.Tk()
    root.title('TCP File Transfer')
    
    canvas1 = tk.Canvas(root, width=300, height=300)
    canvas1.pack()
    
    global label1, file_name, entry1, pb, event_object
    entry1 = tk.Entry(root)
    
    canvas1.create_window(150, 120, window=entry1)
    
    button1 = tk.Button(text='Ask for file', command=ask)
    canvas1.create_window(120, 170, window=button1)
    
    button2 = tk.Button(text='Clear', command=clear)
    canvas1.create_window(190, 170, window=button2)
    
    event_object = threading.Event()
    
    label1 = tk.Label(root, text="")
    canvas1.create_window(150, 220, window=label1)
    root.mainloop()
