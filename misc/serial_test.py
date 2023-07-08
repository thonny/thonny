from serial import Serial
import time

"""
Just after plugging in, the device (Huzzah 32) with ESP32 cam firmware
in Linux, doesn't react to Ctrl-C or ENTER when sent via pyserial (including mpremote). In tio it does.

When opening the connection with DTR and RTS being False, it reboots and reacts properly. After this I can
connect even without specifying DTR and RTS.


"""

port="/dev/ttyACM0"

"""
import termios
f = open(port)
attrs = termios.tcgetattr(f)
attrs[2] = attrs[2] & ~termios.HUPCL
termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
f.close()
"""

s = Serial(baudrate=115200, exclusive=True)
s.port = port
s.dtr = True
s.rts = True
s.open()
#print("DTR/RST", s.dtr, s.rts)
time.sleep(0.1)
#print("DTR/RST", s.dtr, s.rts)
print(s.read_all())
print("-----------------")
s.write(b"\x02")
s.flush()
time.sleep(0.1)
out = s.read_all()
print(out)
if not out:
    s.close()
    s.dtr = False
    s.rts = False
    s.open()
    s.write(b"\x02")
    time.sleep(0.1)
    print(s.read_all())
s.close()
