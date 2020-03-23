#!/usr/bin/env python3
import config
import sys
import selectors
import json
import io
import struct
import socket
import traceback
import time
import traceback

from DbHelpers import Api

"""
 ___  ___                               
 |  \/  |                               
 | .  . | ___  ___ ___  __ _  __ _  ___ 
 | |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
 | |  | |  __/\__ \__ \ (_| | (_| |  __/
 \_|  |_/\___||___/___/\__,_|\__, |\___|
                              __/ |     
                             |___/      
"""
class Message:
    """ This is the base class for ClientMessage and ServerMessage. It has all the duplicate 
        functionality from the code we grabbed from realpython.com's tutorial. The tutorial had
        large message classes for client and server, so I created a base message class so that 
        the client and server classes would be much smaller.  
    """
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            if config.debug:
                print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        self.spec_read()

    def spec_read(self):
        """ Specific Read: This is an abstract method that each client and server much
            implement, since they do slightly different things for each read. 
        """
        pass

    def write(self):
        """ Each client and server do different things for a write(), so this again
            is an abstract method that gets implemented by the child.
        """
        pass

    def close(self):
        if config.debug:
            print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for", f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_server_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received request", repr(self.request), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")



""" 
  _____                         ___  ___                               
 /  ___|                        |  \/  |                               
 \ `--.  ___ _ ____   _____ _ __| .  . | ___  ___ ___  __ _  __ _  ___ 
  `--. \/ _ \ '__\ \ / / _ \ '__| |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
 /\__/ /  __/ |   \ V /  __/ |  | |  | |  __/\__ \__ \ (_| | (_| |  __/
 \____/ \___|_|    \_/ \___|_|  \_|  |_/\___||___/___/\__,_|\__, |\___|
                                                             __/ |     
                                                            |___/      
"""
class ServerMessage(Message):
    """ServerMessage:
    Extends: Message
    Description: Adds necessary server message functionality. In our case, packaging a response
                 and interacting with mongo db. 
    """
    def __init__(self, selector, sock, addr,db=None):
        super().__init__(selector, sock, addr)  # call parent constructor
        self.db = db    
        self.request = None
        self.response_created = False

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        self._write()
    
    def spec_read(self):
        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def process_request(self):
        self.process_server_request()

    def query_api(self):
        """
        This is where our database is communicated with. I would move this elsewhere
        but without rewriting a lot more code, I decided to just keep it here.
        """

        # Simply passes on the "clients" request (built from key=value pairs on command line)
        api = Api(self.db,self.request)
        # Gets result from database class (and uses it in the response to client)
        result = api.processRequest()
        return result

    def create_response(self):
        # Get our query results from the database
        result = self.query_api()

        if self.jsonheader["content-type"] == "text/json":
            # building response to send to client
            content_encoding = "utf-8"
            response = {
                "content_bytes": self._json_encode(result, content_encoding),
                "content_type": "text/json",
                "content_encoding": content_encoding,
            }
        else:
            # Binary or unknown content-type
            response = {
                "content_bytes": b"First 10 bytes of request: "
                + self.request[:10],
                "content_type": "binary/custom-server-binary-type",
                "content_encoding": "binary",
            }

        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

"""
  _____ _ _            _  ___  ___                               
 /  __ \ (_)          | | |  \/  |                               
 | /  \/ |_  ___ _ __ | |_| .  . | ___  ___ ___  __ _  __ _  ___ 
 | |   | | |/ _ \ '_ \| __| |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
 | \__/\ | |  __/ | | | |_| |  | |  __/\__ \__ \ (_| | (_| |  __/
  \____/_|_|\___|_| |_|\__\_|  |_/\___||___/___/\__,_|\__, |\___|
                                                       __/ |     
                                                      |___/      
"""
class ClientMessage(Message):
    def __init__(self, selector, sock, addr, request):
        super().__init__(selector, sock, addr)
        self._request_queued = False
        self.request = request
        self.response = None

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def spec_read(self):
        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)

            if config.debug:
                print("received response", repr(self.response), "from", self.addr)

            #self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            print(f'Unknown content type: received {self.jsonheader["content-type"]} response from', self.addr,)
            #self._process_response_binary_content()
        # Close when response has been processed
        self.close()

