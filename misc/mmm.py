import time

import serial

code = """
s = %r
print()
print(len(s), set(s))
""" % ("*" * 1850)

#s = serial.Serial("/dev/ttyUSB0", 115200)
s = serial.Serial("/dev/ttyACM0", 115200)

s.write(b"\x03")
time.sleep(0.2)
s.write(b"\x03")
s.write(b"\x01")

print(s.read_until(b">"))
s.write(code.encode())
s.flush()
time.sleep(0.1)
s.write(b"\x04")

while True:
    print(s.read(1).decode(), end="")


