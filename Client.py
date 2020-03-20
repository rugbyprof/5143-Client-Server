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
import config
import sys
from ClientClass import Client
from ClientClass import Request
from helpers import myArgParse
import json

def Usage():
    print("Usage: <host> <port> <action> <value>")
    print(f"Example: {sys.argv[0]} host=10.0.61.34 port=6000 action=search value=rhino")
    sys.exit()


if __name__ == "__main__":
    """ Main client driver. 
 
    """
    kwargs, args = myArgParse(sys.argv)
    # print(kwargs,args)

    # get items from command line OR load them from config file
    host = kwargs.get("host", config.host)          # MANDATORY 
    port = int(kwargs.get("port", config.port))     # MANDATORY Port to connect to (XXXXX, e,g, 6000)
    db = kwargs.get("db", config.database)  


    action = kwargs.get("action", None)             # MANDATORY Tells backend what to do: (search,insert, etc.) 

    # The variables below are optional depending on what you are doing. 
    key = kwargs.get("key", None)                   # optional 
    value = kwargs.get("value", None)               # optional
    collection = kwargs.get("collection", None)     # optional
    data = kwargs.get("data", None)                 # optional
    params = kwargs.get("params",None)

    # Create an instance of our "Request" class
    request = Request()

    # if not (host and port and action) or (key or value):
    #     Usage()

    request = request.createRequest(action=action, key=key, collection=collection, data=data, value=value, params=params)

    client = Client(host, port)
    client.start_connection(request)
    response = client.get_response()
    print(response)
