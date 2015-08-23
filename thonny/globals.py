# -*- coding: utf-8 -*-

_worbench = None

def register_workbench(workbench):
    global _workbench
    _workbench = workbench


def get_workbench():    
    return _workbench
    