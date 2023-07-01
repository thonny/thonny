import tkinter as tk
import ctypes

root = tk.Tk()
root.lift()
root.geometry("800x600")

value = 1

hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19

# try with DWMWA_USE_IMMERSIVE_DARK_MODE
result = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                                       ctypes.byref(ctypes.c_int(value)),
                                                       ctypes.sizeof(ctypes.c_int(value)))
if result != 0:
    print("got", result)
    # try with DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20h1
    result = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                                               ctypes.byref(ctypes.c_int(value)),
                                               ctypes.sizeof(ctypes.c_int(value)))
    print("got", result)

root.mainloop()
