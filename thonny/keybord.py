import tkinter as tk
import ctypes
import platform

def get_keyboard_layout():
    """Detect the current keyboard layout"""
    if platform.system() == "Windows":
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        hkl = user32.GetKeyboardLayout(0)
        lang_id = hkl & 0xFFFF  # Extract the language ID
        return lang_id
    else:
        return None  # Handling for non-Windows OS can be added

def on_key_press(event):
    """Handle key events and normalize shortcuts"""
    layout = get_keyboard_layout()
    
    # Hebrew language ID in Windows is 1037 (0x040D)
    if layout == 1037:  
        key_map = {
            "צ": "c",  # Hebrew equivalent of 'C'
            "ף": "x",  # Hebrew equivalent of 'X'
            "ן": "v",  # Hebrew equivalent of 'V'
        }
        if event.keysym in key_map:
            new_keysym = key_map[event.keysym]
            event.widget.event_generate(f"<<{new_keysym.upper()}>>")


root = tk.Tk()
root.bind("<Control-KeyPress>", on_key_press)

label = tk.Label(root, text="Try Ctrl+C, Ctrl+X, Ctrl+V with Hebrew layout")
label.pack(pady=20)

root.mainloop()
