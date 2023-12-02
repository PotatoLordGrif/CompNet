import socket
import sys
import os
from datetime import datetime
BUFFER_SIZE = 1024

class FTP():
    def __init__(self,FTP_IP=None,FTP_PORT=None):
        self.last_call = datetime.utcnow()
        try:
            if FTP_IP == None or FTP_PORT == None:
                self.connected = False
                self.timedout = False
            else:
                self.connected = True
                self.timedout = False
                self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    self.server.connect((FTP_IP,FTP_PORT))
                    self.server.settimeout(60)
                    print("Connection Successful")
                except:
                    print("Connection Failed.")
                self.server.send(sys.getsizeof("CONN").to_bytes(2,"big"))
                self.server.recv(BUFFER_SIZE)
                self.server.send("CONN".encode())
                resp = self.server.recv(BUFFER_SIZE).decode()
                if resp == "CONF":
                    print("Server Confirmed Connection")
        except socket.timeout:
            self.timedout = True
            self.connected = False
            print("Socket timed out!")
    
    def checkTime(self):
        if (datetime.utcnow() - self.last_call).total_seconds() < 60:
            print("Updating last_call", (datetime.utcnow() - self.last_call).total_seconds())
            self.last_call = datetime.utcnow()
        else:
            print("Timed out connection detected!")
            self.timedout = True
            self.connected = False

    def upload(self,file_path,file_name):
        self.server.send(sys.getsizeof("UPLOAD").to_bytes(2,"big"))
        self.server.send("UPLOAD".encode())
        while self.server.recv(BUFFER_SIZE).decode() != "PREP":
            print("Waiting...")
        #print("Received PREP")
        try:
            file = open(file_path + file_name,"rb")
            self.server.send(sys.getsizeof(file_name).to_bytes(2,"big"))
            self.server.send(file_name.encode())
        except:
            print("Couldn't find file...")
            return
        while self.server.recv(BUFFER_SIZE).decode() != "RECV":
            print("Waiting...")
        try:
            self.server.send(os.path.getsize(file_path + file_name).to_bytes(4,"big"))
        except:
            print("Failed..")
        while self.server.recv(BUFFER_SIZE).decode() != "CONF":
            print("Waiting...")
        print(f"Sending {file_name}")
        try:
            b = file.read(BUFFER_SIZE)
            while b:
                self.server.send(b)
                b = file.read(BUFFER_SIZE)
            file.close()
        except:
            print("Something went wrong!")
        while self.server.recv(BUFFER_SIZE).decode() != "FIN":
            print("Waiting for finish")
        return 1
        
    def download(self,file_path,file_name):
        #Initialize Download by sending Req to Server
        self.server.send(sys.getsizeof("DOWNLOAD").to_bytes(2,"big"))
        self.server.send("DOWNLOAD".encode())
        new_file = open(file_path + file_name,"wb")
        #Wait for server to be ready to receive
        while self.server.recv(BUFFER_SIZE).decode() != "PREP":
            print("Waiting...")
        #print("Received PREP")
        #Send name of requested file
        self.server.send(sys.getsizeof(file_name).to_bytes(4,"big"))
        self.server.send(file_name.encode())
        #Wait for server to send file size
        file_bytes = int.from_bytes(self.server.recv(4),"big",signed=True)
        recv_bytes = 0
        #Check to make sure file is available.
        if file_bytes == -1:
            return "File Does Not Exist"
        #Tell server ready to receive bytes
        self.server.send("SEND".encode())
        while recv_bytes < file_bytes:
            b = self.server.recv(BUFFER_SIZE)
            new_file.write(b)
            recv_bytes += BUFFER_SIZE
        new_file.close()
        self.server.send("FIN".encode())
        return 1
        
    def list_files(self):
        self.server.send(sys.getsizeof("LIST").to_bytes(2,"big"))
        self.server.send("LIST".encode())
        #Wait for server to be ready to receive
        file_count = int.from_bytes(self.server.recv(2),"big")
        files = []
        while len(files) < file_count:
            files.append(self.server.recv(BUFFER_SIZE).decode())
        self.server.send("CONF".encode())
        return files

    def delfile(self,remote_file):
        self.server.send(sys.getsizeof("DELETE").to_bytes(2,"big"))
        self.server.send("DELETE".encode())
        while self.server.recv(BUFFER_SIZE).decode() != "PREP":
            print("Waiting...")
        self.server.send(remote_file.encode())
        if self.server.recv(BUFFER_SIZE).decode() == "CONDEL":
            return "Delete Success"
        else:
            return "File Not Found"
    
    def quit(self):
        #print("Sending Quit Command")
        self.server.send(sys.getsizeof("QUIT").to_bytes(2,"big"))
        self.server.send("QUIT".encode())
        if self.server.recv(BUFFER_SIZE).decode() == "CLOSE":
            self.server.close()
            #print("Successfully Closed Connection")
            return
        else:
            #print("Server failed on return.. Closing Connection Forcibly")
            self.server.close()
            return
