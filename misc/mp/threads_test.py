import pyboard
import time

thread_script = """
import machine
from machine import Pin
import time
import _thread

thread_done = False

def ltask(blinks,delay):
    global thread_done
    #led = Pin(25, Pin.OUT)
    for i in range(blinks):
        #led.high()
        #time.sleep(delay)
        #led.low()
        print("uhu")
        time.sleep(delay)
    print("CPU1 Done")
    thread_done = True

_thread.start_new_thread(ltask, (10, 0.2))

# The problem can be avoided by joining the thread before returing:
# while not thread_done:
#     pass

"""

direct_script = """
import machine
from machine import Pin
import time
import _thread

def ltask(blinks,delay):
    led = Pin(25, Pin.OUT)
    for i in range(blinks):
        led.high()
        time.sleep(delay)
        led.low()
        time.sleep(delay)
    print("CPU1 Done")

ltask(10, 0.2)
"""

second_script = """
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
print("let's just take up some space")
"""

pb = pyboard.Pyboard("/dev/ttyACM0")
print("Got connection")
pb.enter_raw_repl()
pb.exec_(thread_script, data_consumer=print)
#pb.exec_(direct_script, data_consumer=print)

time.sleep(15)
pb.serial.read_all() # Othewise exec_ gets confused by the output of the thread
pb.enter_raw_repl()

pb.exec_(second_script, data_consumer=print)
pb.exec_("print('__thonny_helper' in dir())", data_consumer=print)

