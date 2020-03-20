#!/usr/local/Cellar/python@3.8/3.8.1/bin/python3
""" Server.py
Look at above shebang and make sure your python is at same location.
You can test by typing `which python3` at your console.

Description:
    Listens at indicated ip address and port for incoming requests.
Requires:
    ServerClass.py
Usage:
    Configure server using key value pairs: 
    ./Server.py host=10.0.61.34 port=6000
"""
import config
import sys
from helpers import myArgParse
from ServerClass import Server


def Usage():
    print("Usage: <host> <port> <db name>")
    print(f"Example: {sys.argv[0]} host=10.0.61.34 port=6000 db=stockmarket")
    sys.exit()

if __name__=='__main__':
    """ Server driver. It uses ServerClass.py to start listening <host> <port>
        Requires:
            ServerClass.py
        Usage:
            Pass in values to the client using key value pairs 
            ./Server.py host=10.0.61.34 port=6000 db=stockmarket
    """
    # Get key value pairs from command line (see usage)
    kwargs,args = myArgParse(sys.argv)

    db = kwargs.get("db",config.database)          # db = mongodb database name
    host = kwargs.get("host",config.host)      # host = ip address
    port = int(kwargs.get("port",config.port)) # port = chosen port

    # print how to use if both values not on command 
    if not (db and host and port):
        Usage()

    # actually start listening
    server = Server(db,host,port)
    server.run_server()

 
