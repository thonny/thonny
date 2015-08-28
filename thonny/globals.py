# -*- coding: utf-8 -*-

_worbench = None
_runner = None

def register_workbench(workbench):
    global _workbench
    _workbench = workbench

def register_runner(runner):
    global _runner
    _runner = runner


def get_workbench():    
    return _workbench

def get_runner():    
    return _runner
    