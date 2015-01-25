# -*- coding: utf-8 -*-

import sys
import webbrowser
import platform

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny import misc_utils

#TODO - consider moving the cmd_find method to main class in order to pass the editornotebook reference
#TODO - direction support, default down
#TODO - logging
#TODO - instead of text.see method create another one which attempts to center the line where the text was found
#TODO - test on mac and linux

# Handles the find dialog display and the logic of searching. Communicates with the codeview that is passed to the constructor as a parameter.

class FindDialog(tk.Toplevel): 
    def __init__(self, parent): #constructor
        tk.Toplevel.__init__(self, parent, borderwidth=15, takefocus=1) #superclass constructor

        self.codeview = parent; 
        self._init_found_tag_styles();  #sets up the styles used to highlight found strings         
        self.passive_found_tags = set() #references to the current set of passive found tags e.g. all words that match the searched term but are not the active string
        self.active_found_tag = None    #reference to the currently active (centered) found string
    
        #TODO - refactor this, there must be a better way
        try:
            FindDialog.last_searched_word = FindDialog.last_searched_word   #if find dialog was used earlier then the memorized search word is put to the Find entry field
        except:
            FindDialog.last_searched_word = None #if this variable does not exist then this is the first time find dialog has been launched
            
        self.last_found_index = None    #index of the string found during the last search action
        self.last_search_case = None    #case sensitivity value used during the last search


        #set up window display
        self.geometry("+%d+%d" % (parent.winfo_rootx() + parent.winfo_width() // 2,
                                  parent.winfo_rooty() + parent.winfo_height() // 2 - 150))

        self.title("Find")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(parent) 
        self.grab_set()        
        self.protocol("WM_DELETE_WINDOW", self._ok)
      
        #Find text label
        self.find_label = ttk.Label(self, text="Find:");    #TODO - text to resources package
        self.find_label.grid(column=0, row=0);

        #Find text field
        self.find_entry = ttk.Entry(self);
        self.find_entry.grid(column=1, row=0, columnspan=2, padx=5);
        if FindDialog.last_searched_word != None:
            self.find_entry.insert(0, FindDialog.last_searched_word)
        self.find_entry.focus_force();

        #Info text label (invisible by default, used to tell user that searched string was not found etc)
        self.infotext_label_var = tk.StringVar();
        self.infotext_label_var.set("");
        self.infotext_label = ttk.Label(self, textvariable=self.infotext_label_var, foreground="red"); #TODO - style to conf
        self.infotext_label.grid(column=0, row=1, columnspan=3,pady=3);

        #Case checkbox
        self.case_var = tk.IntVar()
        self.case_checkbutton = tk.Checkbutton(self,text="Case sensitive",variable=self.case_var);  #TODO - text to resources
        self.case_checkbutton.grid(column=0, row=2)

        #don't see much point in the button currently, maybe to be added later
        #self.findnext_button = ttk.Button(self, text="OK", command=self._perform_find)
        #self.findnext_button.grid(column=0, row=1)
        
        self.bind('<Escape>', self._ok)
        self.find_entry.bind('<Return>', self._perform_find)
        self.wait_window()

    #returns whether the next search is case sensitive based on the current value of the case sensitivity checkbox
    def _is_search_case_sensitive(self):
        return self.case_var.get() != 0

    #returns whether the current search is a repeat of the last searched based on all significant values
    def _repeats_last_search(self, tofind):
        return tofind == FindDialog.last_searched_word and self.last_found_index != None and self.last_search_case == self._is_search_case_sensitive();

    
    #performs the find action
    def _perform_find(self, event=None): #event needed so just the .bind method doesn't complain
        self.infotext_label_var.set("");    #reset the info label text
        tofind = self.find_entry.get().strip(); #get the text to find 
        if len(tofind) == 0:    #in the case of empty string, cancel
            return              #TODO - set warning text to info label?

        if self._repeats_last_search(tofind): #continuing previous search, find the next occurrence
            search_start_index = self.codeview.text.index("%s+1c" % self.last_found_index);     #start searching from where the previous search left off
            self.codeview.text.tag_remove("currentfound", self.active_found_tag[0], self.active_found_tag[1]);  #remove the active tag from the previously found string
            self.passive_found_tags.add((self.active_found_tag[0], self.active_found_tag[1]))                   #..and set it to passive instead
            self.codeview.text.tag_add("found", self.active_found_tag[0], self.active_found_tag[1]);
            

        else: #start a new search, start from the current insert line position
            if self.active_found_tag != None:
                self.codeview.text.tag_remove("currentfound", self.active_found_tag[0], self.active_found_tag[1]); #remove the previous active tag if it was present
            for tag in self.passive_found_tags:
                self.codeview.text.tag_remove("found", tag[0], tag[1]);                                            #and remove all the previous passive tags that were present
            search_start_index = self.codeview.text.index("insert");    #start searching from the current insert position
            self._find_and_tag_all(tofind);                             #set the passive tag to ALL found occurences
            FindDialog.last_searched_word = tofind;                     #set the data about last search
            self.last_search_case = self._is_search_case_sensitive();       
        
        
        wordstart = self.codeview.text.search(tofind, search_start_index, nocase = not self._is_search_case_sensitive()); #performs the search and sets the start index of the found string
        if len(wordstart) == 0:
            self.infotext_label_var.set("Not found!"); #TODO - better text, also move it to the texts resources list
            return
        
        self.last_found_index = wordstart; #sets the data about last search      
        self.codeview.text.see(wordstart); #moves the view to the found index #TODO - make a new method to center the found line if possible
        wordend = self.codeview.text.index("%s+%dc" % (wordstart, len(tofind))); #calculates the end index of the found string
        self.codeview.text.tag_add("currentfound", wordstart, wordend); #tags the found word as active
        self.active_found_tag = (wordstart, wordend);

    #called when the window is closed. responsible for handling all cleanup. 
    def _ok(self, event=None):
        for tag in self.passive_found_tags:
            self.codeview.text.tag_remove("found", tag[0], tag[1]); #removes the passive tags

        if self.active_found_tag != None:
            self.codeview.text.tag_remove("currentfound", self.active_found_tag[0], self.active_found_tag[1]); #removes the currently active tag   
        
        self.destroy()

    #finds and tags all occurences of the searched term
    def _find_and_tag_all(self, tofind): 
        #TODO - to be improved so only whole words are matched - surrounded by whitespace, parentheses, brackets, colons, semicolons, points, plus, minus

        if self._repeats_last_search(tofind):   #nothing to do, all passive tags already set
            return

        currentpos = 1.0;
        end = self.codeview.text.index("end");

        #searches and tags until the end of codeview
        while True:
            currentpos = self.codeview.text.search(tofind, currentpos, end, nocase = not self._is_search_case_sensitive()); 
            if currentpos == "":
                break

            endpos = self.codeview.text.index("%s+%dc" % (currentpos, len(tofind)))
            self.passive_found_tags.add((currentpos, endpos))
            self.codeview.text.tag_add("found", currentpos, endpos);
            
            currentpos = self.codeview.text.index("%s+1c" % currentpos);

    #initializes the tagging styles 
    def _init_found_tag_styles(self):
        self.codeview.text.tag_configure("found", foreground="green", underline=True) #TODO - style
        self.codeview.text.tag_configure("currentfound", foreground="white", background="red")  #TODO - style