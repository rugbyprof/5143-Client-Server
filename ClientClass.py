#!/usr/bin/env python3
import sys
import selectors
import json
import io
import struct
import socket
import traceback

from Message import ClientMessage

"""
 ______                           _   
 | ___ \                         | |  
 | |_/ /___  __ _ _   _  ___  ___| |_ 
 |    // _ \/ _` | | | |/ _ \/ __| __|
 | |\ \  __/ (_| | |_| |  __/\__ \ |_ 
 \_| \_\___|\__, |\__,_|\___||___/\__|
               | |                    
               |_|                    
"""
class Request:
    """This class builds an appropriate json request for the client to send. 
       It makes sure all requests are formatted the same.  
    """
    def __init__(self):
        self.request = {}
        self.request["type"] = "text/json"
        self.request["encoding"] = "utf-8"
        self.request['content'] = {}

    def createRequest(self, **kwargs):
        """ Loops through kwargs and pulls out all key value pair creating
        a python dictionary to be sent to the server as json
        """
        for k,v in kwargs.items():
            self.request["content"][k] = v
            
        return self.request

"""
  _____ _ _            _   
 /  __ \ (_)          | |  
 | /  \/ |_  ___ _ __ | |_ 
 | |   | | |/ _ \ '_ \| __|
 | \__/\ | |  __/ | | | |_ 
  \____/_|_|\___|_| |_|\__|
                           
"""
class Client:
    def __init__(self, host=None, port=None,debug=False):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.debug = debug
        self.response = None

        if not self.host:
            self.host = config.host
        
        if not self.port:
            self.port = int(config.port)

    def start_connection(self, request):
        addr = (self.host, self.port)
        if self.debug:
            print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = ClientMessage(self.sel, sock, addr, request)
        self.sel.register(sock, events, data=message)

        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
            self.response = message.response

    def get_response(self):
        return self.response
