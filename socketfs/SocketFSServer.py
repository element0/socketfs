#!/usr/bin/env python3

from fs import open_fs
from fs.errors import ResourceNotFound
import json

import socket
import sys
import os
import ipaddress

import logging as logging_default

MAXBUFSIZE=8192

class SocketFSServer():
    def __init__(self,
                 socket_addr,
                 filesystem,
                 logging=logging_default):
        self._socket_addr = socket_addr
        self._fs = filesystem
        self._open_files = dict()
        self._next_fd = 1
        self.logging=logging
        self.logging.debug("SocketFSServer initialized.")


    def get_open_file_fd(self):
        res = self._next_fd
        self._next_fd += 1
        return res

    
    def forever(self):
        target_fs = self._fs
        try:
            os.unlink(self._socket_addr)
        except OSError:
            if os.path.exists( self._socket_addr):
                raise
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self._socket_addr)

        sock.listen(1)
        while True:
            connection,client_address = sock.accept()
            try:
                while True:
                    query = connection.recv( MAXBUFSIZE)
                    if query:
                        cleaned = query.decode().strip()
                        self.logging.debug(f'SocketFSServer: query cleaned: {cleaned}')
                        rq = json.loads( cleaned)

                        for verb in rq:
                            argv = rq[verb]
                            res = "OK"
                            if verb == "ls":
                                res = json.dumps(target_fs.listdir(argv[0]))

                            if verb == "getinfo":
                                res = json.dumps(
                                    target_fs.getinfo(*argv).raw
                                )

                            if verb == "openbin":
                                fd = self.get_open_file_fd()
                                self.open_files[fd] = target_fs.openbin(
                                    *argv
                                )
                                res = f"{fd}"

                            if verb == "close":
                                fd = int(argv[0])
                                self.open_files[fd].close()
                                self.open_files.pop(fd)

                            if verb == "create":
                                res = target_fs.create(*argv)

                            if verb == "readline":
                                fd = int( argv[0])
                                res = self.open_files[fd].readline()

                            if verb == "readbytes":
                                res = target_fs.readbytes(*argv)

                            if verb == "setinfo":
                                target_fs.setinfo(*argv)

                            if verb == "mkdir":
                                target_fs.makedir(*argv)

                            if verb == "rm":
                                target_fs.remove(*argv)

                            if verb == "rmdir":
                                target_fs.removedir(*argv)

                            if verb == "writetext":
                                try:
                                    res = target_fs.writetext(*argv)
                                except Exception as e:
                                    self.logging.debug(f"writetext threw an exception: {e}")
                                    
                            if verb == "processRequest":
                                try:
                                    _res = target_fs.processRequest(*argv)
                                    res = json.dumps(_res)
                                except Exception as e:
                                    self.logging.debug(f"processRequest: Exception: {e}")
                                    res = json.dumps({'processRequest': f'Exception: {e}'})




                            self.logging.debug(str(res))
                            if type(res) == bytes:
                                connection.send(res)
                            else:
                                connection.send(f"{res}\n".encode())
                    else:
                        break
            finally:
                connection.close()

