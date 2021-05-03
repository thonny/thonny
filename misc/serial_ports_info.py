from adafruit_board_toolkit._list_ports_windows import comports
from serial.tools.list_ports import comports

for p in comports():
    #if "VID" in p.hwid:
        for key in ["device", "name", "description", "hwid", "vid", "pid", "serial_number",
                    "location", "manufacturer", "product", "interface"]:
            print(key + ":", getattr(p, key))
        print("-------------")
    
