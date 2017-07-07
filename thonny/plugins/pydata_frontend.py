# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from thonny.plugins.object_inspector2 import ContentInspector
from thonny.gridtable import ScrollableGridTable
from thonny.globals import get_workbench
from thonny.ui_utils import VerticallyScrollableFrame

class DataFrameExplorer(VerticallyScrollableFrame):
    def __init__(self, master):
        
        VerticallyScrollableFrame.__init__(self, master)
        self.colframe = self.interior
        self.demo()
    
    def demo(self):
        
        col_names = ['pers_id', 'stud_id', 'first_name', 'last_name', 'subject', 'lab_group', 'faculty', 'study_level', 'study_year', 'moodle_email', 'sex', 'birth_dt', 'ascii_name', 'feedback_group', 'homework', 'bonus', 'prog_test', 'read_test', 'prog_test_retake', 'read_test_retake', 'mid1_first', 'mid1_retake', 'mid1', 'mid2', 'end_test', 'lab_points', 'exam_points', 'total_points', 'fast_track_points', 'completed_fast_track', 'mid2_ex0_passed', 're_mid1', 're_mid2', 're_mid2_ex0', 're_mid2_ex0_passed', 're_end_test', 'effective_total_points', 're_effective_total_points', 'grade', 're_grade', 'final_mid1', 'final_mid2', 'final_end_test', 're_total_points', 'final_grade', 'final_total_points', 'final_effective_total_points', 'quizzes_attempted', 'start_level', 'learned_school', 'learned_friend', 'learned_myself', 'completed_maalahe', 'completed_alused', 'completed_arvutimang', 'completed_teaduskool', 'completed_other_web', 'completed_any_web_course', 'prog_ambitions1', 'oblig_ambitions1', 'use_more_effective1', 'use_less_effective1', 'use_detects_typos1', 'use_more_thorough1', 'use_too_picky1', 'use_more_motivation1', 'use_less_motivation1', 'use_no_effect_on_process1', 'use_wish_more_detailed_expectations1', 'should_not_limit_times1', 'should_not_limit_freq1', 'should_report_expected1', 'should_report_actual1', 'vpl_comments1', 'general_comments1', 'like_programming', 'final_progress', 'satisfied', 'learn_lecture', 'learn_lab', 'learn_consultation', 'learn_textbook', 'learn_homework', 'like_homework', 'autotest_helped', 'instructor_helped', 'missed_autotest', 'bothered_restrictions', 'bothered_inequality', 'self_test_thoroughness', 'use_more_effective2', 'use_less_effective2', 'use_detects_typos2', 'use_more_thorough2', 'use_too_picky2', 'use_more_motivation2', 'use_less_motivation2', 'use_no_effect_on_process2', 'use_wish_more_detailed_expectations2', 'should_not_limit_times2', 'should_not_limit_freq2', 'should_report_expected2', 'should_report_actual2', 'vpl_comments2', 'prog_ambitions2', 'oblig_ambitions2']
        
        #self.update_columns(3)
    
    def load_dataframe(self, info):
        print("Got info:", info)
    
    def update_columns(self, attributes):
        def create_link(text, row, col):
            link = ttk.Label(self.colframe,
                            wraplength=100,
                            text=text,
                            #background=CALM_WHITE,
                            foreground="blue",
                            cursor="hand2")
            link.grid(row=row, column=col, sticky="nsew", pady=(0,1), padx=(0,1))
        
        def create_title(text, col, colspan=1):
            label = ttk.Label(self.colframe, text=text)
            label.grid(row=0, column=col, columnspan=colspan, sticky="nsew")
        
        
        create_title("Plot by", 0, 2)
        create_title("Column name", 2)
        create_title("min", 3)
        create_title("max", 4)
        create_title("range", 8)
        
        self.vars = []
        import random
        for i, name in enumerate(col_names):
            row = i + 1
            var1 = tk.BooleanVar(self, value=False)
            self.vars.append(var1)
            cb = ttk.Checkbutton(self.colframe, text="", takefocus=False
                                , variable=var1
                                , onvalue=True, offvalue=False
                                )
            cb.grid(row=row, column=0, sticky="nsew", pady=(0,1))
            
            var2 = tk.BooleanVar(self, value=False)
            self.vars.append(var2)
            cb = ttk.Checkbutton(self.colframe, text="", takefocus=False
                                , variable=var2
                                , onvalue=True, offvalue=False
                                )
            cb.grid(row=row, column=1, sticky="nsew", pady=(0,1), padx=(0,1))
            
            create_link(name, row, 2)
            
            
            create_link(str(random.randint(0,10)), row, 3)
            create_link(str(random.randint(40,4000)), row, 4)
            
            create_link("88", row, 8)
            
        
        self.colframe.columnconfigure(8, weight=1)
        
        

class DataFrameInspector(ContentInspector, tk.Frame):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        tk.Frame.__init__(self, master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.table = None
        self.columns = None
        self.index = None
        self.values = None
    
    def set_object_info(self, object_info):
        if self.table is not None and self.columns != object_info["columns"]:
            self.table.grid_forget()
            self.table.destroy()
            self.table = None
        
        data = []
        self.columns = object_info["columns"]
        index = object_info["index"]
        values = object_info["values"]
        assert len(values) == len(index)
        for i in range(len(values)):
            data.append([index[i]] + values[i])
        
        headers = [""] + self.columns 
        
        if self.table is None:
            self.table = ScrollableGridTable(self, [headers],
                                             object_info["row_count"], 0, 1)
            
            self.table.grid(row=0, column=0, sticky="nsew")
        
        self.table.grid_table.set_data(data)
    
    def applies_to(self, object_info):
        return object_info.get("is_DataFrame", False)

def listen_toplevel_results(event):
    if getattr(event, "show_dfe", False):
        view = get_workbench().show_view("DataFrameExplorer")
        info = getattr(event, "dataframe_info")
        if info is not None:
            view.load_dataframe(info)

def load_early_plugin():
    get_workbench().add_content_inspector(DataFrameInspector)


def load_plugin():
    get_workbench().add_view(DataFrameExplorer, "DataFrame explorer", "ne")
    get_workbench().bind("ToplevelResult", listen_toplevel_results, True)
