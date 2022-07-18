#!/usr/bin/python3.9

from socketserver import BaseServer, TCPServer, ThreadingMixIn, \
      StreamRequestHandler
import ssl
import socket
import time
import sys
import threading

class SimpleMessageStorage:

    def __init__(self, expiry=600):
        """expiry is seconds a message is valid."""
        self.messages = []
        self.expiry = expiry
        self._lock = threading.Lock()

    def add_message(self, message):
        self._acquire_lock()
        self.messages.append((time.time(), message))
        self._release_lock()

    def _acquire_lock(self):
        """Acquires a lock on the message database."""
        print("Locking message database")
        self._lock.acquire()

    def _release_lock(self):
        """Acquires a lock on the message database."""
        print("Releasing message database")
        self._lock.release()

    def get_messages(self):
        """Returns a list of messages that are still valid, and
           clears out old messages."""
        new_messages = []
        self._acquire_lock()
        for timestamp, message in self.messages:
            if timestamp < (time.time() + self.expiry):
                new_messages.append((timestamp, message))
        self.messages = new_messages
        self._release_lock()
        return self.messages

message_storage = SimpleMessageStorage()

class Handler(StreamRequestHandler):

    def handle(self):
        global message_storage
        try:
            while True:
                input = self.request.recv(1024)
                input = input.decode("utf-8")
                print("From client:", input)
                message_storage.add_message(input)
                self.wfile.write("Message accepted".encode())
                time.sleep(2)
                if input.lower().strip() == "list":
                   print("Listing messages")
                   messages = ""
                   for timestamp, message in message_storage.get_messages():
                       messages += "%f,%s\n" % (timestamp, message)
                   self.wfile.write(messages.encode())
                if input.lower().strip() == "quit":
                   print("Exiting")
                   self.server.shutdown()
        except Exception as instance:
            print("Exception", type(instance), instance.args, instance)

class Server(ThreadingMixIn, TCPServer):

    daemon_threads = True

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
