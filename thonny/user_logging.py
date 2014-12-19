import ast
import os.path
from time import strptime
from datetime import datetime, timedelta

USER_LOGGER = None # Main will create the logger

"""
TODO: on Mac when playing around with backspace and undo by long pressing keys (long backspace)
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/tkinter/__init__.py", line 1487, in __call__
    return self.func(*args)
  File "/Users/aivar/workspaces/python_stuff/thonny/src/codeview.py", line 445, in smart_backspace_event
    text.delete("insert-1c")
  File "/Users/aivar/workspaces/python_stuff/thonny/src/codeview.py", line 787, in _user_text_delete
    TextWrapper._user_text_delete(self, index1, index2)
  File "/Users/aivar/workspaces/python_stuff/thonny/src/ui_utils.py", line 364, in _user_text_delete
    log_user_event(TextDeleteEvent(self, index1, index2))
  File "/Users/aivar/workspaces/python_stuff/thonny/src/user_logging.py", line 94, in log_user_event
    USER_LOGGER.log_micro_event(e)
  File "/Users/aivar/workspaces/python_stuff/thonny/src/user_logging.py", line 55, in log_micro_event
    and int(self.last_position.split(".")[0]) == int(e.to_position.split(".")[0])
ValueError: invalid literal for int() with base 10: ''
"""

class UserEventLogger:
    def __init__(self, filename=None):
        self.filename = filename
        self.macro_events = []
        self.last_position = "0.0"
        self.last_source = None
        self.default_timeout = timedelta(seconds = 2)
    
    def log_micro_event(self, e):
        # TODO: save and clear the log when it becomes too big
        self.macro_events.append((e, datetime.now()))
        """
        TODO:
        try:
            #print("OK", e, vars(e))
            self._log_micro_event(e)
        except:
            print(self.last_position, e, vars(e))
            raise
        """
    
    def _log_micro_event(self, e):
        # Jätab meelde eelmise event'i klassi nime.
        if(isinstance(e, LoadEvent) or isinstance(e,PasteEvent) or isinstance(e, CutEvent)
           or isinstance(e, UndoEvent) or isinstance(e, RedoEvent)):
            self.last_source = e
        if(isinstance(e, KeyPressEvent)):
            self.last_source = e
        # Koondab üksikud tähesisestused samal real olevatega, va. kui sisestuskursori asukoht on mujal
        # või kui mikrosündmuste vahel on rohkem, kui üleval märgitud default_timeout'is
        elif(isinstance(e, TextInsertEvent)):
            e.source = self.last_source.__class__.__name__
            if(isinstance(self.last_source, KeyPressEvent)):
                if(self.last_source.char == '\r'):
                    e.position = str(self.last_source.cursor_pos.split(".")[0])+ "." + str(int(self.last_source.cursor_pos.split(".")[1]) + 1)
            if(len(self.macro_events) != 0):
                if(isinstance(self.macro_events[-1][0], TextInsertEvent)
                        and int(self.last_position.split(".")[0]) == int(e.position.split(".")[0])
                        and int(self.last_position.split(".")[1]) + 1 == int(e.position.split(".")[1])
                        and datetime.now() - self.macro_events[-1][1] < self.default_timeout):
                    self.macro_events[-1][0].text = self.macro_events[-1][0].text + e.text
                    self.macro_events[-1] = (self.macro_events[-1][0], datetime.now())
                    self.last_position = e.position
                else:
                    self.macro_events.append((e, datetime.now()))
                    self.last_position = e.position
            else:
                self.macro_events.append((e, datetime.now()))
                self.last_position = e.position
        # Koondab üksikud kustutamised samal real tehtutega, va. kui sisestuskursori asukoht on mujal
        # või kui mikrosündmuste vahel on rohkem, kui üleval märgitud default_timeout'is
        elif(isinstance(e, TextDeleteEvent)):
            e.source = self.last_source.__class__.__name__
            if(isinstance(self.last_source, KeyPressEvent) and e.to_position == ''):
                e.to_position = e.from_position.split(".")[0] + "." + str(int(e.from_position.split(".")[1])+1)
                e.from_position = e.from_position.split(".")[0] + "." + str(int(e.from_position.split(".")[1]))
            if(len(self.macro_events) != 0):
                if(isinstance(self.macro_events[-1][0], TextDeleteEvent)
                            and int(self.last_position.split(".")[0]) == int(e.to_position.split(".")[0])
                            and int(self.last_position.split(".")[1]) - 1 == int(e.from_position.split(".")[1])
                            and datetime.now() - self.macro_events[-1][1] < self.default_timeout):
                    e.to_position = self.macro_events[-1][0].to_position
                    self.macro_events[-1] = (e, datetime.now())
                    self.last_position = e.from_position
        #Koondab delete klahvi kustutamised, mis toimuvad samal real va. kui sisestuskursori asukoht on mujal
        # või kui mikrosündmuste vahel on rohkem, kui üleval märgitud default_timeout'is
                elif(isinstance(self.macro_events[-1][0], TextDeleteEvent)
                     and isinstance(self.last_source, KeyPressEvent)
                     and self.last_source.keysym == 'Delete'
                     and int(self.last_position.split(".")[0]) == int(e.to_position.split(".")[0])
                     and int(self.last_position.split(".")[1]) == int(e.from_position.split(".")[1])
                     and datetime.now() - self.macro_events[-1][1] < self.default_timeout):
                    pass
                    e.to_position = self.macro_events[-1][0].to_position.split(".")[0] + "." + str(int(self.macro_events[-1][0].to_position.split(".")[1])+1)
                    self.macro_events[-1] = (e, datetime.now())
                    self.last_position = e.from_position
                else:
                    self.macro_events.append((e, datetime.now()))
                    self.last_position = e.from_position
            else:           
                self.macro_events.append((e, datetime.now()))
                self.last_position = e.from_position            
        else:
            self.macro_events.append((e, datetime.now()))
            
    def save(self):
        """
        Stores whole log into file. 
        This method can be called repeatedly, in this case
        the old version of the file will be just overridden.
        """
        f = open(self.filename, mode="w", encoding="UTF-8")
        for (e, t) in self.macro_events:
            f.write(str(e) +" at " + t.isoformat() + "\n")
        
        f.close()

def log_user_event(e):
    USER_LOGGER.log_micro_event(e)

def events_list_to_json():
    pass

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
    def __init__(self, editor, event, cursor_pos):
        self.editor_id = id(editor)
        self.cursor_pos = cursor_pos
        self.char = event.char
        self.keysym = event.keysym

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
        self.cmd_id = cmd_id
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
    
    #attributes = {
    #    'event_kind' : event_kind,
    #    'event_time' : strptime(right, "%Y-%m-%dT%H:%M:%S.%f")
    #}
    
    constructor_arguments = {}
    
    for kw in tree.body.keywords:
    #    attributes[kw.arg] = ast.literal_eval(kw.value)
        name = kw.arg
        if name == "editor_id":
            name = "editor"
        constructor_arguments[name] = ast.literal_eval(kw.value)
    
    obj = event_class(**constructor_arguments)
    obj.event_time = strptime(right, "%Y-%m-%dT%H:%M:%S.%f")
    
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

