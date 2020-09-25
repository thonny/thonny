import serial
import time

PORT = "/dev/ttyACM0"

# The output of following code tells me whether the code was received intact or not
code = """
print("*" * 1000)
"""

s = serial.Serial(PORT, 115200)

def forward_until(marker):
    total = b""
    while not total.endswith(marker):
        b = s.read(1)
        total += b
        print(b.decode("UTF-8"), end="")

# prepare
print("Interrupting...")
s.write(b"\x03")
s.write(b"\x03")
print("Cleaning...", s.read_all())
s.write(b"\x02")
s.read_until(b">>> ")
print("Got normal prompt")


start_time = time.time()
for i in range(100):
    # goto paste mode
    s.write(b"\x05")
    forward_until(b"=== ")

    data = b"print('*' * 1000)\n"
    s.write(data)
    s.flush()

    # read echo
    forward_until(data)

    # submit the command
    s.write(b"\x04")

    # wait until response
    forward_until(b">>> ")

print("Processing took %.1f seconds", time.time() - start_time)
