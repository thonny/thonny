import serial
import time

PORT = "/dev/ttyACM0"

CTRL_C = b"\x03"
NORMAL_MODE_CMD = b"\x02"
PASTE_MODE_CMD = b"\x05"
EOT = b"\x04"
BLOCK_SIZE = 64


def forward_until(marker, must_include=None):
    total = b""
    while not total.endswith(marker):
        b = s.read(1)
        total += b
        print(b.decode("UTF-8"), end="")

    if must_include and must_include not in total:
        raise RuntimeError("Did not find expected data in the output (%s)"
                           % (total + s.read_all()))


def run_in_paste_mode(source):
    # goto paste mode
    s.write(PASTE_MODE_CMD)
    forward_until(b"=== ")

    while source:
        block = source[:BLOCK_SIZE]
        s.write(block)
        s.flush()
        forward_until(block.replace(b"\r", b"\r=== "))
        source = source[BLOCK_SIZE:]

    s.write(EOT)
    forward_until(b">>> ")

s = serial.Serial(PORT, baudrate=115200)

# interrupt to normal prompt
s.write(CTRL_C)
s.write(CTRL_C)
time.sleep(0.1)
s.read_all()
s.write(NORMAL_MODE_CMD)
forward_until(b">>> ")

print("""
--------------
Running first script:
""")

run_in_paste_mode(b"""import _thread
def doit():
    x = 100000
    while x > 0:
        x -= 1
_thread.start_new_thread(doit, ())
""")

print("""
--------------
Running second script:
""")

run_in_paste_mode(b"""
def blah_blah(arg1):
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    x = "asdfasdfasdfasdfasd"
    return arg1 + x

dummy = blah_blah("x")
""")

s.close()
