# Task log

Cole B

# Prompt for map
"look at the thonny file, make a map of the codebase, so that navigation is easy. Requirments include, a genral description of what each subsection within the codebase contains, in terms of attributes and functionality. Send map to a Map.md file"

# Task 1 Change the title of the main user interface window to thonny[yourname]
Checking workbench because map says it covers the UI section, used command f to look for interface, and or, titlebar no luck 
Checked main.py because it seemed logical, idk, not there 
Checked base_file_browser.py because it contained the line "self.title(self.get_title())"
Ran the code, the window was titled <Untitled>, searched for that, found a matching line in misc_utils.py, changed it, didn't update the window, not what i was looking for 
looked at map again, it has to be in workbench somewhere
Command f for window, the term i didn't use the first time 
IT'S HERE!!!!!!! 

def _init_window(self) -> None:
        self.title("ThonnyCole") 
Made Change, didn't effect window so I had to look for another line 
Found Line 3000 within workbench, edit still didnt work, 
there was a pathway error with running Thonny program with changes i had made, had to use AI to figure out how to reroute.

        final time: 29:48 

        AI used after 25:00 

# Task 2 Change the prompt inside the bottom part of the IDE to start with the first letter of your name 
Checking map, and searching for IDE within files 
Nothing
Searching for >>> 
found shell.py code_indent = prompt_font.measure(">>> ") + x_padding in shell.py 
Changed the >>>, didn't work 
found another line in shell.py
self._insert_text_directly(">>> ", prompt_tags) 
edited, worked

final time 8:15 

no ai 
# Task 3 Inside the “Help” menu, change “About Thonny” to “About [Name] Thonny”
Search map, could be in workbench again because it might be UI, or in about.py 
ran search for menu, looking specifically in workbench and about 
nothing for about.[y], I'll have to check it manually 
nothing came up for workbench, but there are two instances of "About Thonny" in About.py 
First one wasn't it
Second wasn't it either, but that can't be right
edited both, it's working now

final time 21:41

no ai

# Task 4 Change the color of the background behind the text to some obviously different color. 
Map says workbench has themes, start there. 
no quite the themes I'm looking for
search for background color within files 
use keyword textbackground
lots of options
found base_ui_themes.py
file configures  "background": "systemWindowBackgroundColor", so if i find where systemWindowBackgroundColor is defined, that might be it 
run def systemWindowBackgroundColor
no luck 
realized that the program currently configures to the settings of the system (I'm so Smart)
back to square 2ish 
Found base_syntax_themes.py
has line default_bg with a hex code 
set hexcode to random greenish color
WORKS!!!!

time 16:48

ai generated green hexcode
no help finding line in code 