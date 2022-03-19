import sys
if sys.platform == "darwin":
    from adafruit_board_toolkit._list_ports_osx import comports
elif sys.platform == "win32":
    from adafruit_board_toolkit._list_ports_windows import comports
else:
    from serial.tools.list_ports import comports

for p in comports():
    #if "VID" in p.hwid:
        for key in ["device", "name", "description", "hwid", "vid", "pid", "serial_number",
                    "location", "manufacturer", "product", "interface"]:
            print(key + ":", getattr(p, key))
        print("-------------")
    
