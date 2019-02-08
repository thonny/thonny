import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("100x80")

path = r"C:\Users\Aivar\Documents\Python\kula\mula"

def string_width(s):
    temp_label = ttk.Label(root, text=s)
    result = temp_label.winfo_reqwidth()
    temp_label.destroy()
    return result

prev_width = 0
updating = False
def publish(event):
    global prev_width
    global updating
    
    if updating:
        return
    
    updating= True
    
    try:
        available = root.winfo_width()
        
        if available < 10 or prev_width == available:
            return
        
        
        for child in root.winfo_children():
            for grchild in child.winfo_children():
                grchild.destroy()
            child.destroy()
        
        line = tk.Frame(root, background="white")
        line.grid(row=0, column=0, sticky="nsew")
        used = 0
        linecount = 1
        colcount = 0
        for i, part in enumerate(path.split("\\")):
            if i > 0:
                label = ttk.Label(line, text="\\")
                label.grid(row=linecount, column=colcount, sticky="w")
                used += label.winfo_reqwidth()
                colcount += 1
                
            
            if used + string_width(part) > available:
                print("new line"
                      #, line.winfo_reqwidth(), label.winfo_reqwidth(), available
                      )
                used = 0 
                colcount = 0
                line = tk.Frame(root, background="red")
                line.grid(row=linecount, column=0, sticky="nsew")
                linecount += 1
                
            label = ttk.Label(line, text=part)
            
            print(i, part, linecount, colcount)
            label.grid(row=linecount, column=colcount, sticky="w")
            used += label.winfo_reqwidth()
            colcount += 1
        
        #root.columnconfigure(1, weight=1)
        root.update()
        prev_width = root.winfo_width()
    finally:
        updating = False

root.bind("<Configure>", publish, True)


root.mainloop()