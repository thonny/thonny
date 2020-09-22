import time

import serial

count = 1870
code = """
s = %r
print()
print(len(s), set(s))
""" % ("*" * count)

s = serial.Serial("/dev/ttyUSB0", 115200)
#s = serial.Serial("COM4", 115200)

s.write(b"\x03")
time.sleep(0.2)
s.write(b"\x03")
s.write(b"\x01")

print(s.read_until(b"exit\r\n>"))
print("here we go")

for i in range(10):
    s.write(code.encode("UTF-8"))
    s.flush()
    s.write(b"\x04")
    print(s.read_until(b"OK"))
    print(s.read_until(b">"))

while True:
    print(s.read(1).decode(), end="")


