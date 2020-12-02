import os.path
from urllib.request import urlopen

hex_url = "https://github.com/microbit-foundation/micropython-microbit-v2/releases/download/v2.0.0-beta.1/micropython-microbit-v2.0.0-beta.1.hex"
target_dir = "/media/annamaa/MICROBIT"
block_size = 8 * 1024

bytes_copied = 0
with urlopen(hex_url) as source:
    target_path = os.path.join(target_dir, "firmware.hex")
    with open(target_path, "wb") as target:
        while True:
            block = source.read(block_size)
            if not block:
                break

            target.write(block)
            target.flush()
            os.fsync(target.fileno())
            bytes_copied += len(block)
            print("Copied", bytes_copied, "bytes")

print("DONE!")

