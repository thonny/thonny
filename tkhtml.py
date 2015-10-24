"""Wrapper for the tkhtml widget from http://tkhtml.tcl.tk/tkhtml.html"""
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

class TkHtml(tk.Widget):
    def __init__(self, master=None, cfg={}, **kw):
        master.tk.call("package", "require", "Tkhtml")
        tk.Widget.__init__(self, master, 'html', cfg, kw)

        # make selection and copying possible
        self._selection_start_node = None
        self._selection_start_offset = None
        self._selection_end_node = None
        self._selection_end_offset = None
        self.bind("<1>", self._start_selection, True)
        self.bind("<B1-Motion>", self._extend_selection, True)
        self.bind("<<Copy>>", self.copy_selection_to_clipboard, True)
        

    def node(self, *arguments):
        return self.tk.call(self._w, "node", *arguments)

    def parse(self, *args):
        self.tk.call(self._w, "parse", *args)

    def reset(self):
        return self.tk.call(self._w, "reset")
    
    def tag(self, subcommand, tag_name, *arguments):
        return self.tk.call(self._w, "tag", subcommand, tag_name, *arguments)
    
    def text(self, *args):
        return self.tk.call(self._w, "text", *args)
    
    def xview(self, *args):
        "Used to control horizontal scrolling."
        if args: return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_moveto(self, fraction):
        """Adjusts horizontal position of the widget so that fraction
        of the horizontal span of the document is off-screen to the left.
        """
        return self.xview("moveto", fraction)

    def xview_scroll(self, number, what):
        """Shifts the view in the window according to number and what;
        number is an integer, and what is either 'units' or 'pages'.
        """
        return self.xview("scroll", number, what)

    def yview(self, *args):
        "Used to control the vertical position of the document."
        if args: return self.tk.call(self._w, "yview", *args)
        coords = map(float, self.tk.call(self._w, "yview").split())
        return tuple(coords)

    def yview_name(self, name):
        """Adjust the vertical position of the document so that the tag
        <a name=NAME...> is visible and preferably near the top of the window.
        """
        return self.yview(name)

    def yview_moveto(self, fraction):
        """Adjust the vertical position of the document so that fraction of
        the document is off-screen above the visible region.
        """
        return self.yview("moveto", fraction)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and
        what. 'number' is an integer, and 'what' is either 'units' or 'pages'.
        """
        return self.yview("scroll", number, what)
    
    def _start_selection(self, event):
        self.focus_set()
        self.tag("delete", "selection")
        self._selection_start_node, self._selection_start_offset = self.node(True, event.x, event.y)
    
    def _extend_selection(self, event):
        # TODO: the selection may actually shrink
        self._selection_end_node, self._selection_end_offset = self.node(True, event.x, event.y)
        self.tag("add", "selection",
            self._selection_start_node, self._selection_start_offset,
            self._selection_end_node, self._selection_end_offset)
    
    def _ctrl_c(self, event):
        if self.focus_get() == self:
            self.copy_selection_to_clipboard()

    
    def copy_selection_to_clipboard(self, event=None):
        start_index = self.text("offset", self._selection_start_node, self._selection_start_offset)
        end_index = self.text("offset", self._selection_end_node, self._selection_end_offset)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        whole_text = self.text("text")
        selected_text = whole_text[start_index:end_index]
        self.clipboard_clear()
        self.clipboard_append(selected_text)

if __name__ == "__main__":
    root = tk.Tk()
    
    html = TkHtml(root, fontscale=0.8)
    vsb = tk.Scrollbar(root, orient=tk.VERTICAL, command=html.yview)
    hsb = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=html.xview)
    html.configure(yscrollcommand=vsb.set)
    html.configure(xscrollcommand=hsb.set)
    
    
    
    #html.tag("configure", "selection", "-background", "black")

    html.grid(row=0, column=0, sticky=tk.NSEW)
    vsb.grid(row=0, column=1, sticky=tk.NSEW)
    hsb.grid(row=1, column=0, sticky=tk.NSEW)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    html.parse("""
    <html>
    <body>
    <h1>Hello world!</h1>
    <p>First para</p>
    <ul>
        <li>first list item</li>
        <li>second list item</li>
    </ul>
    </body>
    </html>    
    """)
    
    root.mainloop()
