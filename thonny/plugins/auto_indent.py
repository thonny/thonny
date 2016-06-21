"""Example of monkey-patching approach"""

from thonny import roughparse, tktextext
from thonny.codeview import CodeViewText

def patched_perform_return(self, event):
    # copied from idlelib.EditorWindow (Python 3.4.2)
    # slightly modified
    
    text = event.widget
    assert text is self
    
    first, last = text.get_selection_indices()
    try:
        if first and last:
            text.delete(first, last)
            text.mark_set("insert", first)
        line = text.get("insert linestart", "insert")
        i, n = 0, len(line)
        while i < n and line[i] in " \t":
            i = i+1
        if i == n:
            # the cursor is in or at leading indentation in a continuation
            # line; just inject an empty line at the start
            text.insert("insert linestart", '\n')
            return "break"
        indent = line[:i]
        # strip whitespace before insert point unless it's in the prompt
        i = 0
        
        #last_line_of_prompt = sys.ps1.split('\n')[-1]
        while line and line[-1] in " \t" : #and line != last_line_of_prompt:
            line = line[:-1]
            i = i+1
        if i:
            text.delete("insert - %d chars" % i, "insert")
        # strip whitespace after insert point
        while text.get("insert") in " \t":
            text.delete("insert")
        # start new line
        text.insert("insert", '\n')

        # adjust indentation for continuations and block
        # open/close first need to find the last stmt
        lno = tktextext.index2line(text.index('insert'))
        y = roughparse.RoughParser(text.indentwidth, text.tabwidth)
        
        for context in roughparse.NUM_CONTEXT_LINES:
            startat = max(lno - context, 1)
            startatindex = repr(startat) + ".0"
            rawtext = text.get(startatindex, "insert")
            y.set_str(rawtext)
            bod = y.find_good_parse_start(
                      False,
                      roughparse._build_char_in_string_func(startatindex))
            if bod is not None or startat == 1:
                break
        y.set_lo(bod or 0)

        c = y.get_continuation_type()
        if c != roughparse.C_NONE:
            # The current stmt hasn't ended yet.
            if c == roughparse.C_STRING_FIRST_LINE:
                # after the first line of a string; do not indent at all
                pass
            elif c == roughparse.C_STRING_NEXT_LINES:
                # inside a string which started before this line;
                # just mimic the current indent
                text.insert("insert", indent)
            elif c == roughparse.C_BRACKET:
                # line up with the first (if any) element of the
                # last open bracket structure; else indent one
                # level beyond the indent of the line with the
                # last open bracket
                text._reindent_to(y.compute_bracket_indent())
            elif c == roughparse.C_BACKSLASH:
                # if more than one line in this stmt already, just
                # mimic the current indent; else if initial line
                # has a start on an assignment stmt, indent to
                # beyond leftmost =; else to beyond first chunk of
                # non-whitespace on initial line
                if y.get_num_lines_in_stmt() > 1:
                    text.insert("insert", indent)
                else:
                    text._reindent_to(y.compute_backslash_indent())
            else:
                assert 0, "bogus continuation type %r" % (c,)
            return "break"

        # This line starts a brand new stmt; indent relative to
        # indentation of initial line of closest preceding
        # interesting stmt.
        indent = y.get_base_indent_string()
        text.insert("insert", indent)
        if y.is_block_opener():
            text.perform_smart_tab(event)
        elif indent and y.is_block_closer():
            text.perform_smart_backspace(event)
        return "break"
    finally:
        text.see("insert")
        text.event_generate("<<NewLine>>")





def load_plugin():
    CodeViewText.perform_return = patched_perform_return
