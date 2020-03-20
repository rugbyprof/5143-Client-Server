#!/usr/local/Cellar/python@3.8/3.8.1/bin/python3
""" Client.py
Look at above shebang and make sure your python is at same location.
You can test by typing `which python3` at your console.

Description:
    Sends a message to a server at indicated ip address and port.
Requires:
    ClientClass.py
Usage:
    Pass in values to the client using key value pairs 
    ./Client.py host=10.0.61.34 port=6000 action=search value=rhino
"""
import sys
from ClientClass import Client
from ClientClass import Request
from helpers import myArgParse
import time

def Usage():
    print("Usage: <host> <port> <action> <value>")
    print(f"Example: {sys.argv[0]} host=10.0.61.34 port=6000 action=search value=rhino")
    sys.exit()

if __name__=='__main__':
    """ Main client driver. 
 
    """
    kwargs,args = myArgParse(sys.argv)
    #print(kwargs,args)

    host = kwargs.get("host",None)
    port = int(kwargs.get("port",None))
    action = kwargs.get("action",None)
    value = kwargs.get("value",None)

    request = Request()

    if not (host and port and action and value):
        Usage()

    while True:

        request = request.createRequest(action=action, key=value)
        client = Client(host,port)
        client.start_connection(request)
        response = client.get_response()
        print(response)
        sleep(.5)

        
