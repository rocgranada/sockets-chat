# Sockets chat - Python CLI

Implementation of a simple Chat with 1 server and N clients in Python with native sockets.

Functionalities:
 - Client can choose username.
 - Client can choose chat room to join.
 - Client sends messages to the chat room.
 - Client recevies messages from the chat room in real time.

## Local execution

1. Start terminal window with server
```
pyhton3 server.py
```
2. Start N parallel terminal windows with client
```
python3 client.py
```
3. As long as you add multiple clients to the same server, they will talk with each other.

