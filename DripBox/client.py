# -*- coding: utf-8 -*-
"""
CSE 3320 Operating Systems | Assignment 4: Networking and Security
                    < CLIENT SIDE SERVICE >
@author: Nabeel Nayyar
"""
# Import GUI Dependencies
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import askokcancel, showwarning, showinfo
from pathlib import Path
import socket
import time
import os

# GUI window properties and instance
Fwin = tk.Tk()
Fwin.title('DripBox File Upload')
Fwin.resizable(False, False)
Fwin.geometry('300x50')
filetypes = (('All files', '*.*'), ('text files', '*.txt'))
filepath = ""
size = 1000000000
SERVER_ADDR = "localhost"
SERVER_PORT_SEND = 8000
BUFFER_SIZE = 4096  # send 4096 bytes each time step
DISK_LOCK = True  # Security Feature to prevent User Actions


def OpenFile():
    filename = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
    # Tokenize to Last File Name

    u_resp = askokcancel(title='Upload File',
                         message=("Do you wish to upload the file: " +
                                  Path(filename).stem + Path(filename).suffix))
    if u_resp:
        global filepath
        filepath = filename
        Fwin.quit()
        return
    else:
        showwarning(title='Warning', message="No file was selected. Program exiting.")
        exit(-1)


# Setting the Open Button for the file explorer
open_button = ttk.Button(Fwin, text='Open a File', command=OpenFile)
open_button.pack(expand=True)
# Run the GUI Application
Fwin.mainloop()

# Establish connection with server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((SERVER_ADDR, SERVER_PORT_SEND))

# Start User Authentication
print("> Log into your DripBox account <")
username = input("Username: ")
password = input("Password: ")
# OSL Authentication
token = username + "<>" + password
clientSocket.send(token.encode())
# Authentication Check
if clientSocket.recv(BUFFER_SIZE) == b'ZzZ':
    # User Authentication
    print("Welcome to Drip Box:")
    cmd = input("DB> ")
    cmd = cmd.split()
    if cmd[0] == "fetch":
        # Server Sends User Receives tok 0 - 1
        time.sleep(2)
        token = cmd[0] + " " + cmd[1]
        print("Attempting to download file: " + cmd[1])
        # Establish connection with server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((SERVER_ADDR, SERVER_PORT_SEND))
        # Sending packets
        clientSocket.send(token.encode())
        # Reset Socket
        clientSocket.close()

        s = socket.socket()
        s.bind((SERVER_ADDR, SERVER_PORT_SEND))
        s.listen(1)
        c, a = s.accept()
        filetodown = open(cmd[1], "wb")
        while True:
            data = c.recv(size)
            if data == b"TXC":
                print("DB > RX From Server completed")
                break
            filetodown.write(data)
        filetodown.close()

    elif cmd[0] == "send":
        time.sleep(2)
        token = cmd[0] + " " + cmd[1]
        print("Attempting to upload file: " + cmd[1])
        # Establish connection with server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((SERVER_ADDR, SERVER_PORT_SEND))
        # Sending packets
        clientSocket.send(token.encode())
        # Reset Socket
        clientSocket.close()

        # Initialize TX Layer
        s = socket.socket()
        s.connect((SERVER_ADDR, SERVER_PORT_SEND))
        filetosend = open(cmd[1], "rb")
        data = filetosend.read(size)
        while data:
            s.send(data)
            data = filetosend.read(size)
        filetosend.close()
        s.send(b"TXC")
        print("DB > TX to server completed.")
        print(s.recv(size))
        s.shutdown(1)
        s.close()
