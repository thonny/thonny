from getpass import getuser
import os
import socket
from time import sleep

from xdg import XDG_RUNTIME_DIR

def get_socket_path():
    base = XDG_RUNTIME_DIR or os.environ.get("TMPDIR", None) or  os.environ.get("appdata", None) or "/tmp"
    path = os.path.join(base, "thonny-%s" % getuser())

    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    if not os.name == 'nt':
        os.chmod(path, 0o700)

    return os.path.join(path, "ipc.sock")


def become_client():
    s = socket.socket(AF_UNIX)
    s.connect(get_socket_path(), 0.1)


def become_server():
    serversocket = socket.socket(socket.AF_UNIX)
    serversocket.bind(get_socket_path())
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
