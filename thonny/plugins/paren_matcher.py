from thonny.globals import get_workbench
import tokenize
import io


_OPENERS = {')': '(', ']': '[', '}': '{'}
_HIGHLIGHT_CONF = ("PAREN_HIGHLIGHT", {"foreground": "Red"})  # highlight tag configuration
_UNDERLINE_CONF = ("UNDERLINE", {"background": "LightGray"})


class ParenMatcher:

    def __init__(self):
        self.text = None
        self._remaining = None
        self.bound_ids = {}

    def _on_change(self, event):
        self.text.tag_remove(_HIGHLIGHT_CONF[0], "1.0", "end")
        self.text.tag_remove(_UNDERLINE_CONF[0], "1.0", "end")

        self._highlight_surrounding()
        self._highlight_unclosed()
    
    def _configure_tags(self):
        self.text.tag_configure(_HIGHLIGHT_CONF[0], **_HIGHLIGHT_CONF[1])
        self.text.tag_configure(_UNDERLINE_CONF[0], **_UNDERLINE_CONF[1])
        self.text.tag_lower(_UNDERLINE_CONF[0])
        self.text.tag_raise("sel")
        

    def _highlight_surrounding(self):
        indices = self.find_surrounding(self.text)
        if None in indices:
            return
        else:
            self._configure_tags()
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[0])
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[1])

    # highlights an unclosed bracket
    def _highlight_unclosed(self):
        # anything remaining in the stack is an unmatched opener
        # since the list is ordered, we can highlight everything starting from the first element
        if self._remaining:
            opener = self._remaining[0]
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

    def find_surrounding(self, text):
                
        stack = []
        opener, closer = None, None
        open_index, close_index = None, None
        
        for t in self._get_paren_tokens(text.get("1.0", "end")):
            if t.string == "" or t.string not in "()[]{}":
                continue
            if t.string in "([{":
                stack.append(t)
            elif len(stack) > 0:
                if stack[-1].string != _OPENERS[t.string]:
                    text.bell()
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
        # used by _highlight_unclosed
        self._remaining = stack
        
        return open_index, close_index
        

    def _is_insert_between_indices(self, index1, index2):
        return self.text.compare("insert", ">=", index1) and \
               self.text.compare("insert-1c", "<=", index2)

    def _on_editor_change(self, event):

        if self.text:
            # unbind events from previous editor's text
            for k, v in self.bound_ids.items():
                self.text.unbind(k, v)

        # get the active text widget from the active editor of the active tab of the editor notebook
        self.text = event.widget.get_current_editor().get_text_widget()
        self._configure_tags()

        # ...and bind the paren checking procedure to that widget's cursor move event
        self.bound_ids["<<CursorMove>>"] = self.text.bind("<<CursorMove>>", self._on_change, True)
        self.bound_ids["<<TextChange>>"] = self.text.bind("<<TextChange>>", self._on_change, True)


def load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    paren_matcher = ParenMatcher()

    nb.bind("<<NotebookTabChanged>>", paren_matcher._on_editor_change, True)
