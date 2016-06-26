from thonny.globals import get_workbench
import tokenize
import io
from thonny.codeview import CodeViewText
from thonny.shell import ShellText


_OPENERS = {')': '(', ']': '[', '}': '{'}
_HIGHLIGHT_CONF = ("PAREN_HIGHLIGHT", {"foreground": "Blue", 
                                       "font" : get_workbench().get_font("BoldEditorFont")})  # highlight tag configuration
_UNDERLINE_CONF = ("UNDERLINE", {"background": "LightGray"})


class ParenMatcher:

    def __init__(self, text):
        self.text = text
        self._configure_tags()

    def update_highlighting(self):
        self.text.tag_remove(_HIGHLIGHT_CONF[0], "1.0", "end")
        self.text.tag_remove(_UNDERLINE_CONF[0], "1.0", "end")

        remaining = self._highlight_surrounding()
        self._highlight_unclosed(remaining)
    
    def _configure_tags(self):
        self.text.tag_configure(_HIGHLIGHT_CONF[0], **_HIGHLIGHT_CONF[1])
        self.text.tag_configure(_UNDERLINE_CONF[0], **_UNDERLINE_CONF[1])
        self.text.tag_lower(_UNDERLINE_CONF[0])
        self.text.tag_raise("sel")
        

    def _highlight_surrounding(self):
        indices, remaining = self._find_surrounding()
        if None not in indices:
            self._configure_tags()
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[0])
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[1])
        
        return remaining

    # highlights an unclosed bracket
    def _highlight_unclosed(self, remaining):
        # anything remaining in the stack is an unmatched opener
        # since the list is ordered, we can highlight everything starting from the first element
        if len(remaining) > 0:
            opener = remaining[0]
            open_index = "%d.%d" % (opener.start[0], opener.start[1])
            self.text.tag_add(_UNDERLINE_CONF[0], open_index, "end")
    
    def _get_paren_tokens(self, source):
        result = []
        try: 
            tokens = tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline)
            for token in tokens:
                if token.string != "" and token.string in "()[]{}":
                    result.append(token)
        except tokenize.TokenError:
            # happens eg when parens are unbalanced
            pass
        
        return result

    def _find_surrounding(self):
                
        stack = []
        opener, closer = None, None
        open_index, close_index = None, None
        
        for t in self._get_paren_tokens(self.text.get("1.0", "end")):
            if t.string == "" or t.string not in "()[]{}":
                continue
            if t.string in "([{":
                stack.append(t)
            elif len(stack) > 0:
                if stack[-1].string != _OPENERS[t.string]:
                    continue
                if not closer:
                    opener = stack.pop()
                    open_index = "%d.%d" % (opener.start[0], opener.start[1])
                    token_index = "%d.%d" % (t.start[0], t.start[1])
                    if self._is_insert_between_indices(open_index, token_index):
                        closer = t
                        close_index = token_index
                else:
                    stack.pop()
        
        return (open_index, close_index), stack
        

    def _is_insert_between_indices(self, index1, index2):
        return self.text.compare("insert", ">=", index1) and \
               self.text.compare("insert-1c", "<=", index2)

class ShellParenMatcher(ParenMatcher):
    pass

def update_highlighting(event=None):
    text = event.widget
    if not hasattr(text, "paren_matcher"):
        if isinstance(text, CodeViewText):
            text.paren_matcher = ParenMatcher(text)
        elif isinstance(text, ShellText):
            text.paren_matcher = ShellParenMatcher(text)
        else:
            return
    
    text.paren_matcher.update_highlighting()

def load_plugin():
    wb = get_workbench()  
    
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind_class("ShellText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("ShellText", "<<TextChange>>", update_highlighting, True)
