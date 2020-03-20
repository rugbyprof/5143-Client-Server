#!/usr/local/Cellar/python@3.8/3.8.1/bin/python3
"""
ServerClass.py
Description:
    This file is the "controller" talking to "Message.py" (where most the work happens).
    It starts the socket connection and then runs the "loop" in which the server listens
    until killed.
Requires:
    Message.py :: ServerMessage
    
    This line:  `message = ServerMessage(self.sel, conn, addr)` is what gives this file message
    handling capability. 
"""
import config
import sys
import selectors
import json
import io
import struct
import socket
import traceback

from Message import ServerMessage

class Server:
    def __init__(self,db=None,host=None,port=None):
        self.db = db
        self.host = host
        self.port = int(port)

        if not self.db:
            self.db = config.database

        if not self.host:
            self.host = config.host
        
        if not self.port:
            self.port = int(config.port)

        self.sel = selectors.DefaultSelector()

    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = ServerMessage(self.sel, conn, addr,self.db)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def run_server(self):
        #host, port = self.host, int(self.port)
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print("listening on", (self.host, self.port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
