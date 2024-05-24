import os
import tkinter as tk

root = tk.Tk()

bg = tk.Frame(root, background="gray")
bg.grid(sticky="nsew", row=0, column=0)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

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

maccolors = """
systemActiveAreaFill

systemAlertBackgroundActive

systemAlertBackgroundInactive

systemAlternatePrimaryHighlightColor

systemAppleGuideCoachmark

systemBevelActiveDark

systemBevelActiveLight

systemBevelInactiveDark

systemBevelInactiveLight

systemBlack

systemButtonActiveDarkHighlight

systemButtonActiveDarkShadow

systemButtonActiveLightHighlight

systemButtonActiveLightShadow

systemButtonFace

systemButtonFaceActive

systemButtonFaceInactive

systemButtonFacePressed

systemButtonFrame

systemButtonFrameActive

systemButtonFrameInactive

systemButtonInactiveDarkHighlight

systemButtonInactiveDarkShadow

systemButtonInactiveLightHighlight

systemButtonInactiveLightShadow

systemButtonPressedDarkHighlight

systemButtonPressedDarkShadow

systemButtonPressedLightHighlight

systemButtonPressedLightShadow

systemChasingArrows

systemDialogBackgroundActive

systemDialogBackgroundInactive

systemDocumentWindowBackground

systemDragHilite

systemDrawerBackground

systemFinderWindowBackground

systemFocusHighlight

systemHighlight

systemHighlightAlternate

systemHighlightSecondary

systemIconLabelBackground

systemIconLabelBackgroundSelected

systemListViewBackground

systemListViewColumnDivider

systemListViewEvenRowBackground

systemListViewOddRowBackground

systemListViewSeparator

systemListViewSortColumnBackground

systemMenu

systemMenuActive

systemMenuBackground

systemMenuBackgroundSelected

systemModelessDialogBackgroundActive

systemModelessDialogBackgroundInactive

systemMovableModalBackground

systemNotificationWindowBackground

systemPopupArrowActive

systemPopupArrowInactive

systemPopupArrowPressed

systemPrimaryHighlightColor

systemScrollBarDelimiterActive

systemScrollBarDelimiterInactive

systemSecondaryHighlightColor

systemSelectedTabTextColor

systemSheetBackground

systemSheetBackgroundOpaque

systemSheetBackgroundTransparent

systemStaticAreaFill

systemToolbarBackground

systemTransparent

systemUtilityWindowBackgroundActive

systemUtilityWindowBackgroundInactive

systemWhite

systemWindowBody

systemControlAccentColor

systemControlTextColor

systemDisabledControlTextColor

systemLabelColor

systemLinkColor

systemPlaceholderTextColor

systemSelectedTextBackgroundColor

systemSelectedTextColor

systemSeparatorColor

systemTextBackgroundColor

systemTextColor

systemWindowBackgroundColor

systemWindowBackgroundColor1

systemWindowBackgroundColor2

systemWindowBackgroundColor3

systemWindowBackgroundColor4

systemWindowBackgroundColor5

systemWindowBackgroundColor6

systemWindowBackgroundColor7


"""

if os.name == "nt":
    source = wincolors
else:
    source = maccolors

colors = [color for color in source.splitlines() if color]
columns = 3

for i, color in enumerate(colors):
    label = tk.Label(bg, text=color, background=color, foreground="red")
    label.grid(row=i//columns, column=i%columns)

root.mainloop()
