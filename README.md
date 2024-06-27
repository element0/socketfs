# socketfs

A pyfilesystem-socket spamwich.


```mermaid

graph TD
    client[SocketFSClient]:::pyfs
    socket( Socket ):::sock
    server[SocketFSServer]:::pyfs

    client --> socket --> server

    classDef pyfs fill:#eeb
    classDef sock fill:#fcc

```


