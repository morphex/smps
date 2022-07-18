#!/usr/bin/python3.9

import socket
import ssl
import time

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.settimeout(10)

ssl_connection = ssl.wrap_socket(connection)
ssl_connection.connect(("localhost", 3322))
ssl_connection.send("Test".encode())

time.sleep(5)

print("From server:", ssl_connection.recv(1024).decode())

time.sleep(2)

ssl_connection.send("list".encode())

time.sleep(5)

messages = ssl_connection.recv(1024).decode()
print("From server:", messages)

messages = ssl_connection.recv(1024).decode()
print("From server:", messages)

ssl_connection.send("QUIT".encode())

time.sleep(5)

ssl_connection.close()
