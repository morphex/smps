#!/usr/bin/python3.9

from socketserver import BaseServer, TCPServer, ThreadingMixIn, \
      StreamRequestHandler
import ssl
import socket
import time
import sys

class Handler(StreamRequestHandler):

    def handle(self):
        try:
            while True:
                input = self.request.recv(1024)
                input = input.decode("utf-8")
                print("From client:", input)
                self.wfile.write("Message accepted".encode())
                time.sleep(2)
                if input.lower() == "quit":
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
