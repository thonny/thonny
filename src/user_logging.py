from datetime import datetime

USER_LOGGER = None # Main will create the logger

class UserEventLogger:
    def __init__(self, filename=None):
        self.filename = filename
        self.macro_events = []
        self.last_position = "0.0"
    
    def log_micro_event(self, e):
        # Koondab üksikud tähesisestused samal real olevatega, va. kui sisestuskursori asukoht on mujal
        if(isinstance(e, TextInsertEvent)):
            if(len(self.macro_events) != 0):
                if(isinstance(self.macro_events[-1][0], TextInsertEvent)
                        and int(self.last_position.split(".")[0]) == int(e.position.split(".")[0])
                        and int(self.last_position.split(".")[1]) + 1 == int(e.position.split(".")[1])):
                    
                    self.macro_events[-1][0].text = self.macro_events[-1][0].text + e.text
                    self.macro_events[-1] = (self.macro_events[-1][0], datetime.now())
                    self.last_position = e.position
                else:
                    self.macro_events.append((e, datetime.now()))
                    self.last_position = e.position
            else:
                self.macro_events.append((e, datetime.now()))
                self.last_position = e.position
        else:
            # print("Appending: " + str(e))
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
    

class TextInsertEvent(UserEvent):
    def __init__(self, editor, position, text, tags):
        self.editor_id = id(editor)
        self.position = position
        self.text = text
        self.tags = tags
        
class TextDeleteEvent(UserEvent):
    def __init__(self, editor, from_position, to_position):
        self.editor_id = id(editor)
        self.from_position = from_position
        self.to_position = to_position

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

