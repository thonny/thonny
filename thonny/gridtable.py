import tkinter as tk
from tkinter import ttk
from thonny.ui_utils import CALM_WHITE
from random import randint
from thonny import ui_utils
import math

class GridTable(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.header_widgets = {}
        self.data_widgets = {}
        self.labels = []
        #self.demo()
        self.update_idletasks()
        print(self.winfo_height())
        self.bind("<Configure>", self.on_configure, True)
        
        self.screen_row_height = 27
        #self.prepare_table(1, 1000, 0, 7, 1)
        self.first_visible_data_row_no = 5
        self.visible_data_row_count = 0
        self.header_rows = {}
        self.data_rows = {}
    
    
    def prepare_table(self, header_row_count, data_row_count, footer_row_count,
                      column_count, frozen_column_count):
        
        self.screen_row_count = 0
        self.data_row_count = data_row_count
        self.column_count = column_count
        self.header_row_count = header_row_count
        self.footer_row_count = footer_row_count
        self.frozen_column_count = frozen_column_count
    
    def update_header_rows(self):
        for row_no in range(self.header_row_count):
            for col_no in range(self.column_count):
                w = self.get_header_widget(self.screen_row_count, col_no)
                w.grid(row=row_no, column=col_no, sticky="nsew", pady=(0,1), padx=(0,1))
                w.configure(text=self.get_header_value(row_no, col_no))
 
        self.screen_row_count = self.header_row_count
    
    def request_data(self, first_row, last_row):
        """Post the request for indicated rows"""
        pass
    
    def set_data_rows(self, data):
        # data is dictionary from row nr. to row
        self.data.extend(data)
        # 2. If this range is currently visible then update widgets
        pass
    
    def get_data_widget(self, screen_row_no, col_no):
        if (screen_row_no, col_no) not in self.data_widgets:
            self.data_widgets[(screen_row_no, col_no)] = tk.Label(self, 
                                                            background=CALM_WHITE, 
                                                            anchor="e", padx=7,
                                                            text="")
            
        return self.data_widgets[(screen_row_no, col_no)]
    
    def get_header_widget(self, row_no, col_no):
        if (row_no, col_no) not in self.header_widgets:
            w = tk.Label(self, anchor="e", padx=7, text="")
            self.header_widgets[(row_no, col_no)] = w 
            
        return self.header_widgets[(row_no, col_no)]
    
    def set_first_visible_data_row_no(self, n):
        self.first_visible_data_row_no = max(min(n, self.data_row_count), 0)
        self.update_data_widgets()
    
    def reset(self):
        for row in self.labels:
            for label in row:
                label.configure(text=str(randint(0,1000)))
    
    
    def _clear_screen_row(self, row_no):
        for widget in self.grid_slaves(row=row_no):
            widget.grid_remove()
    
    def _prepare_screen_rows(self, available_screen_height):
        max_screen_rows = available_screen_height // self.screen_row_height
        target_screen_row_count = max (
            min (
                self.header_row_count + self.data_row_count + self.footer_row_count,
                max_screen_rows
            ),
            self.header_row_count + 1 + self.footer_row_count
        )
        #target_screen_row_count = 30
        
        # remove cells not required anymore ...
        while self.screen_row_count > target_screen_row_count:
            #print("removing")
            self._clear_screen_row(self.screen_row_count-1)
            self.screen_row_count -= 1
        
        # ... or add cells that can be shown
        while self.screen_row_count < target_screen_row_count:
            #print("adding")
            for col in range(self.column_count):
                w = self.get_data_widget(self.screen_row_count, col)
                w.grid(row=self.screen_row_count, column=col, sticky="nsew", pady=(0,1), padx=(0,1))
                
            self.screen_row_count += 1
            
        self.visible_data_row_count = self.screen_row_count - self.header_row_count - self.footer_row_count
        print("space:", available_screen_height, self.screen_row_height, self.visible_data_row_count)
    
    def update_data_widgets(self):
        for screen_row_no in range(self.header_row_count, self.screen_row_count):
            data_row_no = self.first_visible_data_row_no + screen_row_no - self.header_row_count
            if data_row_no == self.data_row_count:
                break
            
            for col_no in range(self.column_count):
                w = self.get_data_widget(screen_row_no, col_no)
                value = self.get_data_value(data_row_no, col_no)
                if value is None:
                    w.configure(text="")
                else:
                    w.configure(text=str(value))
    
    def get_data_value(self, row_no, col_no):
        assert row_no < self.data_row_count
        return str(row_no) + ":" + str(col_no)
                
    def get_header_value(self, row_no, col_no):
        return "Header " + str(row_no) + ":" + str(col_no)
                
    def on_configure(self, event):
        # query row height
        _, _, _, height = self.grid_bbox(row=1)
        if height > 10 and height < 100:
            "self.screen_row_height = height + 2"
            
        #screen_available_height = self.winfo_height()
        
        #print("HE", self.winfo_height(), event.height, self.screen_row_height)
        self._prepare_screen_rows(event.height)
        
        self.update_data_widgets()


class DemoGridTable(GridTable):
    def __init__(self, master):
        GridTable.__init__(self, master)
        
        self.prepare_table(1, 50, 0, 16, 1)
        self.demo_data()
        #self.update_data_widgets()
        self.update_header_rows()
    
    def demo_data(self):
        for h in range(self.header_row_count):
            hr = []
            for i in range(self.column_count):
                hr.append("Header " + str(h) + ":" + str(i) )
            self.header_rows[i] = hr
        
        for r in range(self.data_row_count):
            row = []
            for i in range(self.column_count):
                row.append(str(r) + ":" + str(i))
            self.data_rows[i] = row
            

class ScrollableGridTable(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg=CALM_WHITE)
        
        # set up scrolling with canvas
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self, bg=CALM_WHITE, bd=0, highlightthickness=0,
                           xscrollcommand=hscrollbar.set)
        hscrollbar.config(command=self.canvas.xview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        hscrollbar.grid(row=1, column=0, sticky=tk.NSEW)
        
        # vertical scrollbar performs virtual scrolling
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._vscroll)
        self.vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.interior = tk.Frame(self.canvas, bg=CALM_WHITE)
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0,0, 
                                                    window=self.interior, 
                                                    anchor=tk.NW)
        self.bind('<Configure>', self._configure_interior, True)
        self.bind('<Expose>', self._on_expose, True)
        
        
        self.grid_table = DemoGridTable(self.interior)
        self.grid_table.grid(row=0, column=0, sticky=tk.NSEW)
        
        self._update_vscroll()
    
    def _update_vscroll(self):
        first = self.grid_table.first_visible_data_row_no / self.grid_table.data_row_count
        last = first + self.grid_table.visible_data_row_count / self.grid_table.data_row_count
        print(first, last, self.grid_table.visible_data_row_count)
        self.vscrollbar.set(first, last)
    
    def _vscroll(self, *args):
        print("vscroll", args, self.vscrollbar.get())
        if len(args) == 3 and args[0] == 'scroll':
            amount = int(args[1])
            unit = args[2]
            if unit == "pages":
                amount *= self.grid_table.visible_data_row_count 
                
            self.grid_table.set_first_visible_data_row_no(self.grid_table.first_visible_data_row_no + amount)
        else:
            assert args[0] == "moveto"
            pos = float(args[1])
            top_row = math.floor((self.grid_table.data_row_count - self.grid_table.visible_data_row_count) * pos)
            self.grid_table.set_first_visible_data_row_no(top_row)
            
        self._update_vscroll()
    
    def _on_expose(self, event):
        self.update_idletasks()
        self._configure_interior(event)
    
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth() , self.canvas.winfo_height())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (self.interior.winfo_reqheight() != self.canvas.winfo_height()
            and self.canvas.winfo_height() > 10):
            # update the interior's height to fit canvas
            self.canvas.itemconfigure(self.interior_id,
                                      height=self.canvas.winfo_height())
        
        self._update_vscroll()
        