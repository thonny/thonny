# -*- coding: utf-8 -*-
from __future__ import print_function, division 

import ast
import _ast
import sys
import token
import tokenize
import io


# token element indices (Py2 tokens aren't named tuples)
TYPE = 0
STRING = 1
START = 2
END = 3
#LINE = 4

def extract_text_range(source, text_range):
    lines = source.splitlines(True)
    # get relevant lines
    lines = lines[text_range.lineno-1:text_range.end_lineno]
    
    # trim last and first lines
    lines[-1] = lines[-1][:text_range.end_col_offset]
    lines[0] = lines[0][text_range.col_offset:]
    return "".join(lines)
    

def find_expression(node, text_range):
    if (hasattr(node, "lineno") 
        and node.lineno == text_range.lineno and node.col_offset == text_range.col_offset
        and node.end_lineno == text_range.end_lineno and node.end_col_offset == text_range.end_col_offset
        # expression and Expr statement can have same range
        and isinstance(node, _ast.expr)):
        return node
    else:
        for child in ast.iter_child_nodes(node):
            result = find_expression(child, text_range)
            if result != None:
                return result
        return None
        

def parse_source(source, filename='<unknown>', mode="exec"):
    root = ast.parse(source, filename, mode)
    mark_text_ranges(root, source)
    return root


def get_last_child(node):
    if isinstance(node, ast.Call):
        # TODO: confirm the evaluation order
        if node.kwargs != None:
            return node.kwargs
        elif node.starargs != None:
            return node.starargs
        elif len(node.keywords) > 0:
            return node.keywords[-1]
        elif len(node.args) > 0:
            return node.args[-1]
        else:
            return node.func
            
    elif isinstance(node, ast.BoolOp):
        return node.values[-1]
    
    elif isinstance(node, ast.BinOp):
        return node.right
        
    elif isinstance(node, ast.Compare):
        return node.comparators[-1]
        
    elif isinstance(node, ast.UnaryOp):
        return node.operand
    
    elif (isinstance(node, (ast.Tuple, ast.List, ast.Set))
          and len(node.elts)) > 0:
        return node.elts[-1]
    
    elif (isinstance(node, ast.Dict)
          and len(node.values)) > 0:
        return node.values[-1]
    
    elif (isinstance(node, (ast.Return, ast.Delete, ast.Assign, ast.AugAssign, ast.Yield))
          and node.value != None):
        return node.value
    
    elif isinstance(node, ast.Expr):
        return node.value
    
    elif isinstance(node, ast.Assert):
        if node.msg != None:
            return node.msg
        else:
            return node.test
    
    elif isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
        return True # There is last child, but I don't know which it will be
    
    else:
        return None
    
    # TODO: pick more cases from here:
    """
    (isinstance(node, (ast.IfExp, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
            or isinstance(node, ast.Raise) and (node.exc != None or node.cause != None)
            # or isinstance(node, ast.FunctionDef, ast.Lambda) and len(node.args.defaults) > 0 
            or sys.version_info[0] == 2 and isinstance(node, (ast.Exec, ast.Repr))  # @UndefinedVariable
            or sys.version_info[0] == 2 and isinstance(node, ast.Print)           # @UndefinedVariable
                and (node.dest != None or len(node.values) > 0))
                
            #"TODO: Import ja ImportFrom"
            # TODO: what about ClassDef ???
    """ 
    
    
    

def mark_text_ranges(node, source):
    """
    Node is an AST, source is corresponding source as string.
    Function adds recursively attributes end_lineno and end_col_offset to each node
    which has attributes lineno and col_offset.
    """
    

    def _get_ordered_child_nodes(node):
        if isinstance(node, ast.Dict):
            children = []
            for i in range(len(node.keys)):
                children.append(node.keys[i])
                children.append(node.values[i])
            return children
        elif isinstance(node, ast.Call):
            children = [node.func] + node.args
            
            for kw in node.keywords:
                children.append(kw.value)
            
            if node.starargs != None:
                children.append(node.starargs)
            if node.kwargs != None:
                children.append(node.kwargs)
            
            children.sort(key=lambda x: (x.lineno, x.col_offset))
            return children
        else:
            return ast.iter_child_nodes(node)    
    
    def _fix_triple_quote_positions(root, all_tokens):
        """
        http://bugs.python.org/issue18370
        """
        filtered = filter(lambda tok: tok[TYPE] == token.STRING, all_tokens)
        string_tokens = list(filtered)
        
        def _fix_str_nodes(node):
            if isinstance(node, ast.Str):
                tok = string_tokens.pop(0)
                node.lineno, node.col_offset = tok[START]
                
            for child in _get_ordered_child_nodes(node):
                _fix_str_nodes(child)
        
        _fix_str_nodes(root)
        
        # fix their erroneous Expr parents   
        for node in ast.walk(root):
            if ((isinstance(node, ast.Expr) or isinstance(node, ast.Attribute))
                and isinstance(node.value, ast.Str)):
                node.lineno, node.col_offset = node.value.lineno, node.value.col_offset
     
    def _fix_binop_positions(node):
        """
        http://bugs.python.org/issue18374
        """
        for child in ast.iter_child_nodes(node):
            _fix_binop_positions(child)
        
        if isinstance(node, ast.BinOp):
            node.lineno = node.left.lineno
            node.col_offset = node.left.col_offset

    
    def _extract_tokens(tokens, lineno, col_offset, end_lineno, end_col_offset):
        return list(filter((lambda tok: tok[START][0] >= lineno
                                   and (tok[START][1] >= col_offset or tok[START][0] > lineno)
                                   and tok[END][0] <= end_lineno
                                   and (tok[END][1] <= end_col_offset or tok[END][0] < end_lineno)
                                   and tok[STRING] != ''),
                           tokens))
    
            
    
    def _mark_text_ranges_rec(node, tokens, prelim_end_lineno, prelim_end_col_offset):
        """
        Returns the earliest starting position found in given tree, 
        this is convenient for internal handling of the siblings
        """

        # set end markers to this node
        if "lineno" in node._attributes and "col_offset" in node._attributes:
            tokens = _extract_tokens(tokens, node.lineno, node.col_offset, prelim_end_lineno, prelim_end_col_offset)
            #tokens = 
            _set_real_end(node, tokens, prelim_end_lineno, prelim_end_col_offset)
        
        # mark its children, starting from last one
        # NB! need to sort children because eg. in dict literal all keys come first and then all values
        children = list(_get_ordered_child_nodes(node))
        for child in reversed(children):
            (prelim_end_lineno, prelim_end_col_offset) = \
                _mark_text_ranges_rec(child, tokens, prelim_end_lineno, prelim_end_col_offset)
        
        if "lineno" in node._attributes and "col_offset" in node._attributes:
            # new "front" is beginning of this node
            prelim_end_lineno = node.lineno
            prelim_end_col_offset = node.col_offset
        
        return (prelim_end_lineno, prelim_end_col_offset)

    
    def _strip_trailing_junk_from_expressions(tokens):
        while (tokens[-1][TYPE] not in (token.RBRACE, token.RPAR, token.RSQB,
                                      token.NAME, token.NUMBER, token.STRING)
                    and not (hasattr(token, "ELLIPSIS") and tokens[-1][TYPE] == token.ELLIPSIS) 
                    and tokens[-1][STRING] not in ")}]"
                    or tokens[-1][STRING] in ['and', 'as', 'assert', 'class', 'def', 'del',
                                              'elif', 'else', 'except', 'exec', 'finally',
                                              'for', 'from', 'global', 'if', 'import', 'in',
                                              'is', 'lambda', 'not', 'or', 'try', 
                                              'while', 'with', 'yield']):
            del tokens[-1]
    
    def _strip_trailing_extra_closers(tokens, remove_naked_comma):
        level = 0
        for i in range(len(tokens)):
            if tokens[i][STRING] in "({[":
                level += 1
            elif tokens[i][STRING] in ")}]":
                level -= 1
            
            if level == 0 and tokens[i][STRING] == "," and remove_naked_comma:
                tokens[:] = tokens[0:i]
                return
             
            if level < 0:
                tokens[:] = tokens[0:i]
                return   
    
    def _set_real_end(node, tokens, prelim_end_lineno, prelim_end_col_offset):
        """
        # shortcut
        node.end_lineno = prelim_end_lineno
        node.end_col_offset = prelim_end_col_offset
        return tokens
        """
        # prelim_end_lineno and prelim_end_col_offset are the start of 
        # next positioned node or end of source, ie. the suffix of given
        # range may contain keywords, commas and other stuff not belonging to current node
        
        # Function returns the list of tokens which cover all its children
        
        
        """
        print("\n############################################\n")
        print(node.__class__)
        if isinstance(node, ast.Name):
            print(node.id)
        print(node.lineno, node.col_offset, prelim_end_lineno, prelim_end_col_offset)
        print(" ".join(list(map(lambda x:x[STRING], tokens))))
        print("----------")
        for tok in tokens:
            print(tok)
        """
        if isinstance(node, _ast.stmt):
            # remove empty trailing lines
            while (tokens[-1][TYPE] in (tokenize.NL, tokenize.COMMENT, token.NEWLINE, token.INDENT)
                   or tokens[-1][STRING] in (":", "else", "elif", "finally", "except")):
                del tokens[-1]
                
        else:
            _strip_trailing_extra_closers(tokens, not isinstance(node, ast.Tuple))
            _strip_trailing_junk_from_expressions(tokens)
        
        # set the end markers of this node
        node.end_lineno = tokens[-1][END][0]
        node.end_col_offset = tokens[-1][END][1]
        
        # Try to peel off more tokens to give better estimate for children
        # Empty parens would confuse the children of no argument Call
        if ((isinstance(node, ast.Call)) 
            and not (node.args or node.keywords or node.starargs or node.kwargs)):
            assert tokens[-1][STRING] == ')'
            del tokens[-1]
            _strip_trailing_junk_from_expressions(tokens)
        # attribute name would confuse the "value" of Attribute
        elif isinstance(node, ast.Attribute):
            assert tokens[-1][TYPE] == token.NAME
            del tokens[-1]
            _strip_trailing_junk_from_expressions(tokens)
                
        return tokens
    
    def _tokenize(source):
        if sys.version_info[0] == 2:
            return list(tokenize.generate_tokens(io.StringIO(source).readline))
        else:
            return list(tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline))

    all_tokens = _tokenize(source)
    _fix_triple_quote_positions(node, all_tokens)
    _fix_binop_positions(node)
    source_lines = source.splitlines(True) 
    prelim_end_lineno = len(source_lines)
    prelim_end_col_offset = len(source_lines[len(source_lines)-1])
    _mark_text_ranges_rec(node, all_tokens, prelim_end_lineno, prelim_end_col_offset)
    

    
"""
def _bubble_up_starting_positions(node):
    # this is required for ordering the nodes (see _mark_text_ranges_rec)
    if "lineno" in node._attributes:
        node.start_position = (node.lineno, node.col_offset)
    else:
        node.start_position = None
    for child in ast.iter_child_nodes(node):
        child_pos = _bubble_up_starting_positions(child)
        if node.start_position == None or (child_pos != None and child_pos < node.start_position):
            node.start_position = child_pos
    
    return node.start_position

def _find_minusone_offsets(root):
    for node in ast.walk(root):
        if hasattr(node, "col_offset") and node.col_offset < 0:
            msg = "node has col_offset < 0, " + str((node.__class__, node.lineno, node.col_offset))
            print("$$$$$$", msg)
            #raise AssertionError(msg)

def _find_twisted_locations(root):
    for node in ast.walk(root):
        try:
            if (hasattr(node, "lineno") 
                and (node.lineno > node.end_lineno
                     or node.lineno == node.end_lineno and node.col_offset > node.end_col_offset)):
                import sys
                #msg = "twisted " + str((node.__class__, node.lineno, node.col_offset))
                print("$$$$$$ twisted", node.__class__, node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, file=sys.stderr)
                #raise AssertionError(msg)
        except:
            print("!!!!!!!! missing end location", node.__class__, node.lineno, node.col_offset, file=sys.stderr)
"""


def value_to_literal(value):
    if value == None:
        return ast.Name(id="None", ctx=ast.Load())
    elif isinstance(value, bool):
        if value:
            return ast.Name(id="True", ctx=ast.Load())
        else:
            return ast.Name(id="False", ctx=ast.Load())
    elif isinstance(value, str):
        return ast.Str(s=value)
    else:
        raise NotImplementedError("only None, bool and str supported at the moment, not " + str(type(value)))



    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            source = f.read()
            print("TOKENS") 
            for tok in tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline):
                print(tok)
            print("AST")
            root = ast.parse(source, sys.argv[1])
            for node in ast.walk(root):
                print(node, end=" ")
                if hasattr(node, "lineno"):
                    print(node.lineno, node.col_offset)
                else:
                    print()

            
        
