#!/usr/bin/python3.9

from socketserver import BaseServer, TCPServer, ThreadingMixIn, \
      StreamRequestHandler
import ssl
import socket
import time
import sys
import threading
from sdt import DEBUG_PRINT

class SimpleMessageStorage:

    def __init__(self, expiry=600):
        """expiry is seconds a message is valid."""
        self.messages = []
        self.expiry = expiry
        self._lock = threading.Lock()

    def add_message(self, message):
        self._acquire_lock()
        self.messages.append((time.time(), message))
        # Miniscule sleep period to ensure unique timestamps
        time.sleep(0.00001)
        self._release_lock()

    def _acquire_lock(self):
        """Acquires a lock on the message database."""
        DEBUG_PRINT("Locking message database")
        self._lock.acquire()

    def _release_lock(self):
        """Releases the lock on the message database."""
        DEBUG_PRINT("Releasing message database")
        self._lock.release()

    def get_messages(self):
        """Returns a list of messages that are still valid, and
           clears out old messages."""
        new_messages = []
        self._acquire_lock()
        for timestamp, message in self.messages:
            if timestamp < (time.time() + self.expiry):
                new_messages.append((timestamp, message))
        self.messages = list(new_messages)
        self._release_lock()
        return new_messages

message_storage = SimpleMessageStorage()

class Handler(StreamRequestHandler):

    def handle(self):
        global message_storage
        try:
            while True:
                input = self.request.recv(1024)
                input = input.decode("utf-8")
                DEBUG_PRINT("From client:", input)
                message_storage.add_message(input)
                self.wfile.write("Message accepted".encode())
                if input.lower().strip() == "list":
                   DEBUG_PRINT("Listing messages")
                   messages = ""
                   for timestamp, message in message_storage.get_messages():
                       messages += "%f,%s\n" % (timestamp, message)
                   self.wfile.write(messages.encode())
                if input.lower().strip() == "quit":
                   DEBUG_PRINT("Exiting")
                   self.server.shutdown()
        except Exception as instance:
            DEBUG_PRINT("Exception", type(instance), instance.args, instance)

class Server(ThreadingMixIn, TCPServer):

    daemon_threads = True
    request_queue_size = 1000

    def __init__(self, address=("localhost", 3322), bind_and_activate=True):
        super().__init__(address, Handler, False)

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain("./ssl/cert.pem", keyfile="./ssl/key.pem")

        self.socket = ssl_context.wrap_socket(self.socket, server_side=True)

        if bind_and_activate:
            self.server_bind()
            self.server_activate()

server = Server()
server.serve_forever()
