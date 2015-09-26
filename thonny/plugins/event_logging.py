import os.path
import tkinter as tk
import time
from thonny.globals import get_workbench
from thonny.workbench import WorkbenchEvent
from datetime import datetime
import zipfile 
from tkinter.filedialog import asksaveasfilename


class EventLogger:
    def __init__(self, filename=None):
        self._filename = filename
        self._init_logging()
        self._init_commands()
    
    def _init_commands(self):
        get_workbench().add_command(
            "export_usage_logs",
            "tools",
            "Export usage logs ...",
            self._cmd_export,
            group=60
        )

    
    def _init_logging(self):
        self._encoding = "UTF-8"
        self._file = open(self._filename, mode="a", encoding=self._encoding)
        self._file.write("[\n")
        
        self._event_count = 0
        self._last_event_timestamp = datetime.now()
        
        wb = get_workbench()
        wb.bind("WorkbenchClose", self._on_worbench_close, True)
        
        for sequence in ["<<Undo>>",
                         "<<Redo>>",
                         "<<Cut>>",
                         "<<Copy>>",
                         "<<Paste>>",
                         #"<<Selection>>",
                         #"<Key>",
                         #"<KeyRelease>",
                         "<Button-1>",
                         "<Button-2>",
                         "<Button-3>"
                         ]:
            self._bind_all(sequence)
        
        for sequence in ["Command",
                         "Open",
                         "Save",
                         "SaveAs",
                         "NewFile",
                         "ShellCommand",
                         "ShellInput",
                         "ShowView",
                         "HideView",
                         "TextInsert",
                         "TextDelete",
                         ]:
            self._bind_workbench(sequence)

        self._bind_workbench("<FocusIn>", True)
        self._bind_workbench("<FocusOut>", True)
        
        ### log_user_event(KeyPressEvent(self, e.char, e.keysym, self.text.index(tk.INSERT)))

        
        # TODO: if event data includes an Editor, then look up also text id
    
    def _bind_workbench(self, sequence, only_workbench_widget=False):
        def handle(event):
            if not only_workbench_widget or event.widget == get_workbench():
                self._log_event(sequence, event)
        
        get_workbench().bind(sequence, handle, True)
    
    def _bind_all(self, sequence):
        
        def handle(event):
            self._log_event(sequence, event)
        
        tk._default_root.bind_all(sequence, handle, True)
    
    def _extract_interesting_data(self, event, sequence):
        data = {}
        
        if isinstance(event, tk.Event):
            data["widget_id"] = id(event.widget)
            data["widget_class"] = event.widget.__class__.__name__
            # TODO: add other interesting attributes for individual events
            
        else:
            assert isinstance(event, WorkbenchEvent)
            # save all attributes
            for name in dir(event):
                if not name.startswith("_"):
                    value = getattr(event, name)
                    
                    if isinstance(value, tk.BaseWidget):
                        data[name + "_id"] = id(value)
                        data[name + "_class"] = value.__class__.__name__
                    elif name in ("update", "setdefault"): # TODO: make it more reliable
                        pass
                    elif (isinstance(value, str)
                            or isinstance(value, int)
                            or isinstance(value, float)):
                        data[name] = value
                    
                    else:
                        data[name] = repr(value)
                                 
                        
        
        
        return data
    
    def _cmd_export(self):
        
        filename = asksaveasfilename (
                filetypes =  [('all files', '.*'), ('Zip-files', '.zip')], 
                defaultextension = ".zip",
                initialdir = get_workbench().get_option("run.working_directory"),
                initialfile = time.strftime("ThonnyUsageLogs_%Y-%m-%d.zip")
        )
        
        if not filename:
            return
        
        log_dir = os.path.dirname(self._filename)
        
        with zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for item in os.listdir(log_dir):
                if item.endswith(".txt"):
                    zipf.write(os.path.join(log_dir, item), arcname=item)
            
    
    def _log_event(self, sequence, event):
        
        timestamp = datetime.now()
        time_from_last_event = timestamp-self._last_event_timestamp
        
        data = self._extract_interesting_data(event, sequence)
        data["sequence"] = sequence 
        data["time"] = timestamp.isoformat()
        
        
        if self._event_count > 0:
            self._file.write(",\n")
             
        self._file.write(repr(data))
        
        self._last_event_timestamp = timestamp
        self._event_count += 1
        
        if (self._event_count % 100 == 0
            or time_from_last_event.total_seconds() > 3):
            self._intermediate_save()
    
    
    def _on_worbench_close(self, event=None):
        self._final_save()
    
    def _intermediate_save(self):
        self._file.close()
        self._file = open(self._filename, mode="a", encoding=self._encoding)
    
    def _final_save(self):
        self._file.write("\n]\n")
        self._file.close()

def load_plugin():
    # generate log filename
    folder = os.path.expanduser(os.path.join("~", ".thonny", "user_logs"))
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    for i in range(100): 
        filename = os.path.join(folder, time.strftime("%Y-%m-%d_%H-%M-%S_{}.txt".format(i)));
        if not os.path.exists(filename):
            break
    
    # create logger
    EventLogger(filename)
    