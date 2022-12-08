# -*- coding: utf-8 -*-
"""
DRIPBOX Cloud File System
                    < SERVER SIDE SERVICE >
@author: Nabeel
"""
import socket
import os
from os.path import exists
from datetime import datetime

# Global Variables for the server env
SERVER_DIRECTORY_NAME = "Server_Storage"
SERVER_DOMIAIN = "localhost"
SERVER_PORT = 8000
SERVER_LOCK_MODE = True
USER_TUPLE = ["Sam", "SamE"]
BUFFER_SIZE = 4096  # send 4096 bytes each time step
SYSTEM_SIZE = 1000000000


# create handler for each connection
def ServerConstructor():
    if not os.path.exists(SERVER_DIRECTORY_NAME):
        os.mkdir(SERVER_DIRECTORY_NAME)

    os.chdir(SERVER_DIRECTORY_NAME)


# Default SysGen
ServerConstructor()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Setting up the Server Port and domain
serverSocket.bind((SERVER_DOMIAIN, SERVER_PORT))
serverSocket.listen()

# Accept Connections for Authentication first
while True:
    (clientConnected, clientAddress) = serverSocket.accept()
    dataFromClient = clientConnected.recv(BUFFER_SIZE)
    node = dataFromClient.decode()
    if node == USER_TUPLE[0] + "<>" + USER_TUPLE[1]:
        SERVER_LOCK_MODE = False
        clientConnected.send("ZzZ".encode())
        print("Server ACCEPTED connection from %s:%s" % (clientAddress[0], clientAddress[1]))
        break
    else:
        clientConnected.send("X".encode())
        print("Server REJECTED connection from %s:%s" % (clientAddress[0], clientAddress[1]))

# Socket Reset
serverSocket.close()

# Restarting Socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Setting up the Server Port and domain
serverSocket.bind((SERVER_DOMIAIN, SERVER_PORT))
serverSocket.listen()
(clientConnected, clientAddress) = serverSocket.accept()
dataFromClient = clientConnected.recv(BUFFER_SIZE)
# Now Listen for Access MODE
while True:
    node = dataFromClient.decode()
    serverSocket.close()    # Socket Reset
    print("> RX: " + node)
    node = node.split()
    if node[0] == "fetch":
        # Ensuring that the file is available in the system
        file_exists = exists(node[1])
        if file_exists:
            # Restarting Socket
            s = socket.socket()
            s.connect((SERVER_DOMIAIN, SERVER_PORT))
            filetosend = open(node[1], "rb")
            data = filetosend.read(SYSTEM_SIZE)
            while data:
                s.send(data)
                data = filetosend.read(SYSTEM_SIZE)
            filetosend.close()
            s.send(b"TXC")
            break

    elif node[0] == "send":
        # First Chain of Transmission is sending File Name + Extension
        s = socket.socket()
        s.bind((SERVER_DOMIAIN, SERVER_PORT))
        s.listen(1)
        c, a = s.accept()
        filetodown = open(node[1], "wb")
        while True:
            data = c.recv(SYSTEM_SIZE)
            if data == b"TXC":
                print("DBS > RX from client completed.")
                break
            filetodown.write(data)
        filetodown.close()
        break

print("[!] Server Exited.")
