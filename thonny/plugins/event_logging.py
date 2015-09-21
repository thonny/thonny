import ast
import os.path
import tkinter as tk
import time
from thonny.globals import get_workbench
from thonny.workbench import WorkbenchEvent
from datetime import datetime


class EventLogger:
    def __init__(self, filename=None):
        self._filename = filename
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
                         "<FocusIn>",
                         "<FocusOut>",
                         #"<Key>",
                         #"<KeyRelease>",
                         "<Button-1>",
                         "<Button-2>",
                         "<Button-3>"
                         ]:
            self._bind(sequence)


        #get_workbench().bind("<FocusIn>", self._on_get_focus, "+")
        #get_workbench().bind("<FocusOut>", self._on_lose_focus, "+")
        
        ### log_user_event(KeyPressEvent(self, e.char, e.keysym, self.text.index(tk.INSERT)))

        
        # TODO: if event data includes an Editor, then look up also text id
    
    def _bind(self, sequence, widget=None):
        
        def handle(event):
            self._log_event(sequence, event)
        
        if widget:
            widget.bind(sequence, handle, True)
        else:
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
                    
                    if name == "editor":
                        data["editor_id"] = id(value)
                        
                    elif isinstance(value, tk.BaseWidget):
                        data[name + "_id"] = id(value)
                        data[name + "_class"] = value.__class__.__name__
                    
                    elif (isinstance(value, str)
                            or isinstance(value, int)
                            or isinstance(value, float)):
                        data[name] = value
                    
                    else:
                        data[name] = repr(value)
                                 
                        
        
        
        return data
    
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


class UserEvent:
    def __str__(self):
        keys = sorted(self.__dict__.keys())
        items = ("{}={!r}".format(k, str(self.__dict__[k])) for k in keys)
        return "{}({})".format(self.__class__.__name__.replace("Event", ""), ", ".join(items))
    
    def compact_description(self):
        return self.__class__.__name__.replace("Event", "")

class TextInsertEvent(UserEvent):
    def __init__(self, editor, position, text, tags, source=None):
        self.editor_id = id(editor)
        self.position = position
        self.text = text
        self.tags = tags
        self.source = source
        
class TextDeleteEvent(UserEvent):
    def __init__(self, editor, from_position, to_position, source=None):
        self.editor_id = id(editor)
        self.from_position = from_position
        self.to_position = to_position
        self.source = source

class UndoEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)        
        
class RedoEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class CutEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class PasteEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class CopyEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class RunEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class SaveEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class SaveAsEvent(UserEvent):
    def __init__(self, editor, filename):
        self.editor_id = id(editor)
        self.filename = filename
        
class LoadEvent(UserEvent):
    def __init__(self, editor, filename):
        self.editor_id = id(editor)
        self.filename = filename
        
class NewFileEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class EditorGetFocusEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class EditorLoseFocusEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)

class KeyPressEvent(UserEvent):
    def __init__(self, editor, char, keysym, cursor_pos):
        self.editor_id = id(editor)
        self.cursor_pos = cursor_pos
        self.char = char
        self.keysym = keysym

class CommentInEvent(UserEvent):
    def __init__(self, editor, scope, affected_lines):
        self.editor_id = id(editor)
        self.scope = scope
        self.affected_lines = affected_lines

class CommentOutEvent(UserEvent):
    def __init__(self, editor, scope, affected_lines):
        self.editor_id = id(editor)
        self.scope = scope
        self.affected_lines = affected_lines


# class SelectionChangeEvent(UserEvent):
#     def __init__(self, editor, first_pos, last_pos):
#         self.editor_id = id(editor)
#         self.first_pos = first_pos
#         self.last_pos = last_pos
    
        
class ProgramGetFocusEvent(UserEvent):
    pass
        
class ProgramLoseFocusEvent(UserEvent):
    pass

class CommandEvent(UserEvent):
    def __init__(self, cmd_id, source):
        self._cmd_id = cmd_id
        self.source = source

class ShellCreateEvent(UserEvent):
    def __init__(self, editor):
        self.editor_id = id(editor)
        
class ShellCommandEvent(UserEvent):
    def __init__(self, command_text):
        self.command_text = command_text 

class ShellInputEvent(UserEvent):
    def __init__(self, command_text):
        self.command_text = command_text 
        
class ShellOutputEvent(UserEvent):
    # TODO: distinguish between err and out
    def __init__(self, text):
        self.text = text

# TODO: return object with correct class
def parse_log_line(line):
    split_pos = line.rfind(" at ")
    assert split_pos > 0
    left = line[0:split_pos]
    right = line[split_pos + 4:].strip()
    
    tree = ast.parse(left, mode='eval')
    assert isinstance(tree, ast.Expression)
    assert isinstance(tree.body, ast.Call)
    
    event_kind = tree.body.func.id
    event_class = globals()[event_kind + "Event"]
    
    constructor_arguments = {}
    
    for kw in tree.body.keywords:
        name = kw.arg
        if name == "editor_id":
            name = "editor"
            editor_id = ast.literal_eval(kw.value) # TODO: clean this hack
        constructor_arguments[name] = ast.literal_eval(kw.value)
    
    obj = event_class(**constructor_arguments)
    obj.event_time = datetime.strptime(right, "%Y-%m-%dT%H:%M:%S.%f")
    
    if hasattr(obj, "editor_id"): # TODO: hack
        obj.editor_id = editor_id
    
    return obj

def parse_log_file(filename):
    f = open(filename, encoding="UTF-8")
    events = []
    for line in f:
        events.append(parse_log_line(line))
    
    f.close()
    return events

def parse_all_log_files(path):
    all_events = []
    for name in sorted(os.listdir(path)):
        if name.endswith(".txt"):
            events = parse_log_file(os.path.join(path, name))
            all_events.extend(events)
            
    return all_events

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
    