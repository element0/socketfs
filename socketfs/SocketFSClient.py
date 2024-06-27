import socket
import sys
from fs.base import FS
from fs.info import Info
import json
import logging as logging_default

MAXBUFSIZE=8192


class SocketFSClient(FS):
    def __init__(self,sockaddr,logging=logging_default):
        logging.debug("SocketFSClient::__init__")
        self.sockaddr = sockaddr
        self.logging = logging_default
        super().__init__()

    def close(self):
        pass

    def send_rq(self, rq):
        res = b''
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(self.sockaddr)
            self.logging.debug(f"SocketFSClient::send_rq: rq:{rq}")
            sock.sendall(rq.encode())
            self.logging.debug(f"SocketFSClient::send_rq: sent")

            while True:
                more = sock.recv(MAXBUFSIZE)
                res = res + more
                if len(more) < MAXBUFSIZE:
                    break

            self.logging.debug(f"SocketFSClient::send_rq: received: {res}")
        return res

    def create(self, path, wipe=False):
        if path == None:
            return True
        rq_raw = { "create": [path,wipe] }
        rq = json.dumps(rq_raw)

        res = self.send_rq(rq)
        return json.loads(res)

    def getinfo(self, path, namespaces=None):
        if path == None:
            return Info(dict())
        rq_raw = { "getinfo": [path,namespaces]}
        rq = json.dumps(rq_raw)
        
        res = self.send_rq(rq)
        if res == None:
            self.logging.debug(f"SocketFSClient::getinfo(): expected result, got None")
            return Info(dict())
        self.logging.debug(f"SocketFSClient::getinfo(): res = {res}")
        return Info(json.loads(res.decode()))

    def listdir(self, path):
        rq = '{"ls":["' + path + '"]}'
        res = self.send_rq(rq)
        return json.loads(res.decode())

    # TODO: return type SubFS
    #
    def makedir(self, path, permissions=None, recreate=False):
        rq_raw = { "mkdir": [path,permissions,recreate]}
        rq = json.dumps(rq_raw)
        res = self.send_rq(rq)
        return

    # TODO: return *file-like* object
    #       of type io.IOBase
    def openbin(self, path, mode="r",buffering=-1,**options):
        rqdict = {
            "openbin": [ path, mode, buffering, options ]
        }
        rq = json.dumps(rqdict)
        self.logging.debug(f"SocketFSClient::openbin(): rq: {rq}")
        res = self.send_rq(rq)
        return json.loads(res.decode())

    def readbytes(self, path=None):
        self.logging.debug(f"SocketFSClient::readbytes: path: {path}")
        rqdict = { "readbytes": [ path ] }
        rq = json.dumps(rqdict)
        return self.send_rq(rq)

    def remove(self, path):
        pass

    def removedir(self, path):
        pass

    def setinfo(self, raw):
        pass

    def writetext(self, path, contents, encoding='utf-8', errors=None, newline=''):
        self.logging.debug(f"SocketFSClient::writetext: path: {path}")
        self.logging.debug(f"SocketFSClient::writetext: contents head: {contents[0:100]}")
        rqdict = { "writetext": [ path, contents ] }
        rq = json.dumps(rqdict)
        return self.send_rq(rq)

    def processRequest(self, path, request_json):
        self.logging.debug(f"SocketFSClient::processRequest: path: {path} {request_json}")
        request_raw = { "processRequest": [ path, json.loads(request_json) ] }
        rq = json.dumps(request_raw)
        self.logging.debug(f"SocketFSClient::processRequest: rq: {rq}")
        return self.send_rq(rq)
