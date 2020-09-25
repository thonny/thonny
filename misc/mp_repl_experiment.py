import serial
import time

PORT = "/dev/ttyACM0"

MODE = "paste" # "paste" or "raw"
BLOCK_SIZE = 256
LENGTH_OF_STRING_LITERAL = 1000 # affects the size of the script sent to the device
NUM_ITERATIONS = 10000 # how many times to send the script to the device

# The output of following code tells me whether the code was received intact or not
code = """
s = "%s"
print()
print(len(s), set(s))
""" % ("*" * LENGTH_OF_STRING_LITERAL)

s = serial.Serial(PORT, 115200)

def forward_until(marker):
    total = b""
    while not total.endswith(marker):
        b = s.read(1)
        total += b
        print(b.decode("UTF-8"), end="")

def prepare():
    print("Interrupting...")
    s.write(b"\x03")
    s.write(b"\x03")
    print("Cleaning...", s.read_all())
    s.write(b"\x02")
    s.read_until(b">>> ")
    print("Got normal prompt")


def start_raw_mode():
    s.write(b"\x01")
    forward_until(b"exit\r\n>")
    print("Got raw prompt. Executing code...")


def run_in_raw_mode():
    data = code.encode("UTF-8")
    while data:
        s.write(data[:BLOCK_SIZE])
        s.flush()
        data = data[BLOCK_SIZE:]
        if data:
            time.sleep(0.01)

    s.write(b"\x04")
    forward_until(b"OK")
    # wait until completion
    forward_until(b">")

def run_in_paste_mode():
    # goto paste mode
    s.write(b"\x05")
    forward_until(b"=== ")

    for line in code.splitlines(keepends=True):
        data = line.encode("UTF-8")
        while data:
            block = data[:BLOCK_SIZE]
            s.write(block)
            s.flush()

            forward_until(block)
            #time.sleep(0.01)
            data = data[BLOCK_SIZE:]

    s.write(b"\x04")
    forward_until(b">>> ")

prepare()
start_time = time.time()

if MODE == "raw":
    start_raw_mode()

for i in range(NUM_ITERATIONS):
    print("Iteration", i)
    if MODE == "raw":
        run_in_raw_mode()
    else:
        run_in_paste_mode()

print("Processing took %.1f seconds" % (time.time() - start_time))
