import socket
from time import sleep

port = 4957


def become_client():
    s = socket.create_connection(("localhost", port), 0.1)


def become_server():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(("localhost", port))
    serversocket.listen(5)
    while True:
        (clientsocket, address) = serversocket.accept()
        print("got connection:", clientsocket, address)


become_server()
# become_server()

# try:
#    become_server()
# except OSError:
#    become_client()
