import tkinter as tk

import os

from thonny import get_workbench
from tkinter.messagebox import showinfo
from tkinter import Message, Button
from tkinter.commondialog import Dialog

from thonny.plugins.codelive.session_host import Host
from thonny.plugins.codelive.session_client import Client
from thonny.plugins.codelive.start_up_dialog import StartUpDialog

WORKBENCH = get_workbench()
session = None
DEBUG = True

def start_session():
    # TODO: Configure StartUpDialog class to get basic user info for
    #       the collab session
    # top = StartUpDialog(master=WORKBENCH)
    global session
    #if top.getInfo() == "Host":
    session = Host(1)
   # session.start()
    session.run()
    return (1, "null", 0)

def callback():
    global session
    if session != None:
        session.kill()
        code = "done"
        if DEBUG:
            print("end code:", code)
    else:
        session, session_type, code = start_session()
        if DEBUG:
            print("session type: %s\tcode: %d" % (session_type, code))

def load_plugin():
    WORKBENCH.add_command(command_id = "add_randomItem",
                          menu_name = "CodeLive",
                          command_label = "Start a Live Collaboration Session",
                          handler = callback,
                          position_in_group="end",
                          image=os.path.join(os.path.dirname(__file__), "res/people-yellow-small.png"), 
                          caption = "CodeLive",
                          include_in_toolbar = True,
                          bell_when_denied = True)
