import tkinter as tk

root = tk.Tk()

wincolors = """
system3dDarkShadow

systemHighlight

system3dLight

systemHighlightText

systemActiveBorder

systemInactiveBorder

systemActiveCaption

systemInactiveCaption

systemAppWorkspace

systemInactiveCaptionText

systemBackground

systemInfoBackground

systemButtonFace

systemInfoText

systemButtonHighlight

systemMenu

systemButtonShadow

systemMenuText

systemButtonText

systemScrollbar

systemCaptionText

systemWindow

systemDisabledText

systemWindowFrame

systemGrayText

systemWindowText
"""

for color in wincolors.split():
    label = tk.Label(root, text=color, background=color, foreground="red")
    label.grid()

root.mainloop()
