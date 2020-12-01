
import json
import sys
from threading import Thread, Event, Lock
from queue import Queue
import time
import struct
import pickle

#import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt

#from threading import Thread
#from queue import SimpleQueue

from thonny import get_workbench

WORKBENCH = get_workbench()
QOS = 0
BROKER = 'test.mosquitto.org'
PORT = 1883
exitFlag = Event()
global workQueue
workQueue = Queue(30)

# Precursors for Host class methods
class Host(mqtt.Client):
    def __init__(self, thread_nums):
        super().__init__()
        print("*****")
        print("Initializing connection...")
        print("*****")
        self.threads = []
        self.connect(BROKER, PORT, 60)

        for threadID in range(thread_nums):
            self.threads.append(ProcessThread("Thread"+str(threadID), self))
    
    def run(self):
        for t in self.threads:
            t.start()
    
    def on_connect(self, client, userdata, rc, *extra_params):
        print('Connected with result code='+str(rc))
        self.subscribe("Calvin/CodeLive/Change", qos=QOS)

    def on_message(self, client, data, msg):
        if msg.topic == "Calvin/CodeLive/Change":
            if msg:
                if msg == "END":
                    print("end")
                else:
                    workQueue.put(msg.payload)

    #closes client and terminates threads
    def kill(self):
        print("closing")
        self.close()
        exitFlag.set()
        for t in self.threads:
            t.join()

###################################

class ProcessThread(Thread):
    def __init__(self, name, client):
        Thread.__init__(self)
        self._name = name
        self._editor_notebook = WORKBENCH.get_editor_notebook()

    def send_response(self, client, message):
        (result, num) = client.publish('Calvin/CodeLive/Change', message, qos=QOS)
        print("sent response:", message)
        if result != 0:
            print('PUBLISH returned error:', result)

    def makeChange(self, sock):
        while True:
            msg = workQueue.get()
            if msg:
                codeview = self._editor_notebook.get_current_editor().get_text_widget()
                print("message: %s\t command: %s\tposition: %s\tsrting: %s" % (msg, msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
                if msg[0] == "I":
                    codeview.insert(msg[2:msg.find("]")], msg[msg.find("]") + 1:])
                    pass
                else:
                    pass
            else:
                print("...")
            if exitFlag.is_set():
                break
            time.sleep(.25)

if __name__ == "__main__":
    # Unit Tests
    pass
