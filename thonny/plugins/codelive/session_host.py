import socket
import socketserver
from threading import Thread
from queue import SimpleQueue

from thonny import get_workbench

MSGLEN = 2048
WORKBENCH = get_workbench()

# Precursors for Host class methods

def myreceive(sock):
    chunk = sock.recv(MSGLEN)
    if chunk == b'':
        raise RuntimeError("socket connection broken")
    return chunk

def showReceived(sock):
    active = True
    while active:
        msg = str(myreceive(sock), encoding="ascii")
        if msg == "END":
            active = False
            print("ENDING")
        else:
            
            print("message: %s\t command: %s\tposition: %s\tsrting: %s" % (msg, msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
            
    sock.shutdown(0)

###################################

class Host(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._name = "Hi"
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections = {}
        self._instruction_queue = SimpleQueue()
        self._server.bind(('localhost', 8000))
        self._editor_notebook = WORKBENCH.get_editor_notebook()

    def makeChange(self, sock):
        active = True
        while active:
            msg = str(myreceive(sock), encoding="ascii")
            if msg == "END":
                active = False
                print("ENDING")
            else:
                codeview = self._editor_notebook.get_current_editor().get_text_widget()
                print("message: %s\t command: %s\tposition: %s\tsrting: %s" % (msg, msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
                if msg[0] == "I":
                    codeview.insert(msg[2:msg.find("]")], msg[msg.find("]") + 1:])
                    pass
                else:
                    pass
                
        sock.shutdown(0)

    def run(self):
        self._server.listen(1)

        while True:
            client, add = self._server.accept()
            print("new connection at:", add)
            self.makeChange(client)

if __name__ == "__main__":
    # Unit Tests
    pass
