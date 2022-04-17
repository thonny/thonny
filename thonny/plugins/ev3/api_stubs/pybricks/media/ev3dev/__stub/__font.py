class Font:
    """
    Object that represents a font for writing text.

    The font object will be a font that is the "best" match based on the parameters given and available fonts installed.

    Class Attributes:
        DEFAULT (Font): The default font.

    Attributes:
        family (str): The family of the font.
        style (str): A string describing the font style.
        width (int): The width of the widest character of the set.
        height (int): The height of the font.

    Args:
        family (str): The preferred font family or None to use the default value.
        size (int): The preferred font size. Most fonts have sizes between 6 and 24. This is the “point” size and not the same as height.
        bold (bool): When True, prefer bold fonts.
        monospace (bool): When True prefer monospaced fonts. This is useful for aligning multiple rows of text.
        lang (str): A language code, such as 'en' or 'zh-cn' or None to use the default language. [1]
        script (str): A unicode script identifier such as 'Runr' or None.
    """
    DEFAULT = None  # type: Font

    def __init__(self, family: str = None, size: int = 12, bold: bool = False, monospace: bool = False, lang: str = None, script: str = None):
        self.family = ''  # type: str
        self.style = ''  # type: str
        self.width = 0  # type: int
        self.height = 0  # type: int

    def text_width(self, text: str) -> int:
        """
        Gets the width of the text when the text is drawn using this font.

        Returns:
            The width in pixels.
        """

        return 0

    def text_height(self, text: str) -> int:
        """
        Gets the height of the text when the text is drawn using this font.

        Returns:
            The height in pixels.
        """

        return 0

Font.DEFAULT = Font('Lucida', 12)