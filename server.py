import socket
import sys
import time
import os
from threading import Thread

ADDRESS_BIND = "127.0.0.1"
PORT_BIND = 21 # Generic FTP Port
BUFFER_SIZE = 1024


def on_connection(sock,addr):
    try:
        print(f"New Connection from {addr}")
        sock.settimeout(60)
        len = int.from_bytes(conn.recv(2),"big")
        conn.send(b'1')
        msg = conn.recv(len).decode()
        if msg == "CONN":
            sock.send("CONF".encode())
        while True:
            len = int.from_bytes(conn.recv(2),"big")
            msg = conn.recv(len).decode()
            if msg == "QUIT":
                sock.send("CLOSE".encode())
                break
            elif msg == "UPLOAD":
                upload(sock)
            elif msg == "DOWNLOAD":
                download(sock)
            elif msg == "LIST":
                file_list(sock)
            elif msg == "DELETE":
                delfile(sock)
        print(f"Closing Connection {addr}")
        sock.close()        
    except socket.timeout:
        print("Socket timed out..", {addr})

@socket.timeout
def timeout(socket):
    print("Connection Timed Out")

def upload(sock):
    #Confirm with Client that ready to receive.
    sock.send("PREP".encode())
    #Receive filename
    len = int.from_bytes(conn.recv(2),"big")
    file_name = sock.recv(len).decode()
    uploaded_file = open("./Server/" + file_name,"wb")
    #Ready to receive file content.
    sock.send("RECV".encode())
    #File Size
    file_bytes = int.from_bytes(sock.recv(4),"big")
    sock.send("CONF".encode())
    recv_bytes = 0
    print(f"Receiving {file_name}")
    while recv_bytes < file_bytes:
        b = sock.recv(BUFFER_SIZE)
        uploaded_file.write(b)
        recv_bytes += BUFFER_SIZE
    uploaded_file.close()
    print("Completed Receive, notifying Client.")
    #Notify Client that file was uploaded.
    sock.send("FIN".encode())
    #Return to thread
    return

def download(sock):
    #Send Signal to send File_name
    sock.send("PREP".encode())
    #Recv File Name
    len = int.from_bytes(conn.recv(4),"big")
    file_name = sock.recv(len).decode()
    #Open File as Read
    try:
        print(f"Trying to find {file_name}")
        file = open("./Server/" + file_name,"rb")
    except:
        fail = -1
        sock.send(fail.to_bytes(4,"big",signed=True))
        return
    try:
        sock.send(os.path.getsize("./Server/" + file_name).to_bytes(4,"big"))
    except:
        print("Failed..")
    if sock.recv(BUFFER_SIZE) != "SEND":
        print("Nope")
    print(f"Sending File {file_name}")
    try:
        b = file.read(BUFFER_SIZE)
        while b:
            sock.send(b)
            b = file.read(BUFFER_SIZE)
        file.close()
    except:
        print("File failed to transfer")
        return
    if sock.recv(BUFFER_SIZE) == "FIN":
        return

def file_list(sock):
    files = os.listdir("./Server/")
    sock.send(len(files).to_bytes(2,"big"))
    for file in files:
        sock.send(file.encode())
    if sock.recv(BUFFER_SIZE).decode()  == "CONF":
        print("Sent Files. Returning to main")
        return
    

def delfile(sock):
    sock.send("PREP".encode())
    file_name = sock.recv(BUFFER_SIZE).decode()
    if os.path.isfile("./Server/" + file_name):
        os.remove("./Server/" + file_name)
        sock.send("CONDEL".encode())
    else:
        sock.send("FAILDEL".encode())
    return


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((ADDRESS_BIND,PORT_BIND))

server.listen(5)

while True:
    conn, address = server.accept()
    new_thread = Thread(target=on_connection, args=(conn,address))
    new_thread.start()
server.close()
new_thread.join()