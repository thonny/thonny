import tkinter as tk
from thonny.ui_utils import CALM_WHITE
from random import randint

class GridTable(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.cells = {}
        self.labels = []
        self.demo()
        self.update_idletasks()
        print(self.winfo_height())
        self.bind("<Configure>", self.on_configure, True)
        self.screen_row_count = 5
        self.column_count = 10
        self.data_row_count = 1000
        self.screen_row_height = 20
    
    def get_widget(self, screen_row, screen_col):
        if (screen_row, screen_col) not in self.cells:
            self.cells[(screen_row, screen_col)] = tk.Label(self, background=CALM_WHITE)
            
        return self.cells[(screen_row, screen_col)]
    
    def demo(self):        
        def upd(event):
            print(event.x, event.y)
            self.reset()
            
        for x in range(10):
            row = []
            self.columnconfigure(x, pad=2, minsize=50)
            for y in range(100):
                if x == 0 or y == 0:
                    background=None
                else:
                    background=CALM_WHITE
                box = self.get_widget(x, y)
                box.grid(row=y, column=x, sticky="nsew", padx=1, pady=1)
                box.bind("<1>", upd, True)
                row.append(box)
            
            self.labels.append(row)
        
        for y in range(100):
            self.rowconfigure(y, pad=2)
    
    def reset(self):
        for row in self.labels:
            for label in row:
                label.configure(text=str(randint(0,1000)))
        
    
    def _prepare_screen_rows(self, available_screen_height):
        max_screen_rows = available_screen_height // self.screen_row_height
        target_screen_row_count = max(min(self.data_row_count, max_screen_rows), 3)
        print("target:", target_screen_row_count)
        
        # remove cells not required anymore ...
        while self.screen_row_count > target_screen_row_count:
            for widget in self.grid_slaves(row=self.screen_row_count-1):
                widget.grid_remove()
            self.screen_row_count -= 1
        
        # ... or add cells that can be shown
        while self.screen_row_count < target_screen_row_count:
            for col in range(self.column_count):
                w = self.get_widget(self.screen_row_count, col)
                w.grid(row=self.screen_row_count, column=col)
                
            self.screen_row_count += 1
                
                
    
    def on_configure(self, event):
        print("HE", self.winfo_height())
        self._prepare_screen_rows(self.winfo_height())
