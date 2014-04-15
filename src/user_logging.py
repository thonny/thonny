from datetime import datetime

USER_LOGGER = None # Main will create the logger

class UserEventLogger:
    def __init__(self, filename=None):
        self.filename = filename
        self.macro_events = []
    
    def log_micro_event(self, e):
        # TODO: mõned sündmused tuleks koondada, ja panna koondsündmus macro_events'i
        
        self.macro_events.append((e, datetime.now()))
        print("EVENT:", str(e))
    
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
    

class TextInsertEvent(UserEvent):
    def __init__(self, editor_id, position, text):
        self.editor_id = editor_id
        self.position = position
        self.text = text
        
class TextDeleteEvent(UserEvent):
    def __init__(self, editor_id, from_position, to_position):
        self.editor_id = editor_id
        self.from_position = from_position
        self.to_position = to_position

class UndoEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id        
        
class RedoEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class CutEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class PasteEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class CopyEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class RunEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class SaveEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class SaveAsEvent(UserEvent):
    def __init__(self, editor_id, filename):
        self.editor_id = editor_id
        self.filename = filename
        
class EditorGetFocusEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class EditorLoseFocusEvent(UserEvent):
    def __init__(self, editor_id):
        self.editor_id = editor_id
        
class ProgramGetFocusEvent(UserEvent):
    pass
        
class ProgramLoseFocusEvent(UserEvent):
    pass
        
class ShellExecuteCommandEvent(UserEvent):
    def __init__(self, command_text):
        self.command_text = command_text 
        
class ShellOutputEvent(UserEvent):
    def __init__(self, text):
        self.text = text

