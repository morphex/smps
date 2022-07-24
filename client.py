#!/usr/bin/python3.9

import socket
import ssl
import time
from sdt import DEBUG_PRINT
import _thread
import sys

SLEEP_TIME = 0

try:
    number_of_test_threads = int(sys.argv[1])
except IndexError:
    number_of_test_threads = 100

class Client:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.settimeout(10)
        ssl_connection = ssl.wrap_socket(connection)
        ssl_connection.connect((self.hostname, self.port))
        self._connection = ssl_connection

    def send(self, message):
        """Sends a message and returns the reply."""
        self._connection.send(message.encode())
        return self.receive()

    def receive(self, size=1024):
        """Receives a transmission."""
        return self._connection.recv(size).decode()

    def quit(self):
        self._connection.close()

finished = 0

def _run_client_test(quit=0):
    client = Client("localhost", 3322)
    reply = client.send("Test")
    time.sleep(SLEEP_TIME)
    DEBUG_PRINT("From server:", reply)
    time.sleep(SLEEP_TIME)
    reply = client.send("list")
    time.sleep(SLEEP_TIME)
    DEBUG_PRINT("From server:", reply)
    messages = client.receive()
    DEBUG_PRINT("From server:", messages)
    if quit:
        reply = client.send("QUIT")
        time.sleep(SLEEP_TIME)
        client.quit()
    global finished
    finished += 1

def run_client_test(quit=0):
    try:
        _run_client_test(quit=quit)
    except Exception as exception:
        print("Exception", type(exception), exception.args)
        global finished
        finished += 1

run_client_test()

threads = []
print("Starting threads: ")
for x in range(number_of_test_threads):
    print("%i," % x, end="")
    threads.append(_thread.start_new_thread(run_client_test, ()))
#print(threads)
while True:
    if len(threads) == finished:
        break
    time.sleep(0.01)
print()
print("Finished testing..")
run_client_test(quit=1)
