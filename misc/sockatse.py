import socket

port = 4957

def become_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", port))

def become_server():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(("localhost", port))
    serversocket.listen(5)
    while True:
        (clientsocket, address) = serversocket.accept()
        print("got connection:", clientsocket, address)

try:
    become_server()
except OSError:
    become_client()
