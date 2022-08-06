from pybricks.media.ev3dev import Font, ImageFile
from pybricks.parameters import Color
from typing import Union

empty = None
class Image:
    """
    Object representing a graphics image. This can either be an in-memory copy of an image or the image displayed on a screen.

    Args:
        source (str, Image, or ImageFile): The source of the image.
        sub (bool): If sub is True, then the image object will act as a sub-image of the source image (this only works if the type of source is Image and not when it is a str or ImageFile).

    Attributes:
        width: The width of this image in pixels.
        height: The height of this image in pixels.

    Note:
        If source is a string or ImageFile, then the image will be loaded from the file path given by the string. Only .png files are supported. As a special case, if the string is '_screen_', the image will be configured to draw directly on the screen.

        If an Image is given, the new object will contain a copy of the source image object.

        Additional keyword arguments x1, y1, x2, y2 are needed when sub=True. These specify the top-left and bottom-right coordinates in the source image that will be used as the bounds for the sub-image.
    """

    def __init__(self, source: Union['Image', str, ImageFile], *, sub: bool = False, x1: int = None, y1: int = None, x2: int = None, y2: int = None):
        self.width = 0  # type: int
        self.height = 0  # type: int

    @staticmethod
    def empty(width: int = 178, height: int = 128) -> 'Image':
        """
        Creates a new empty Image object.

        Args:
            width (int): The width of the image in pixels.
            height (int): The height of the image in pixels.

        Returns:
            A new image with all pixels set to Color.WHITE.

        Raises:
            TypeError: width or height is not a number
            ValueError: width or height is less than 1.
            RuntimeError: There was a problem allocating a new image.
        """
        return empty

    def draw_text(self, x: int, y: int, text: str, text_color: Color = Color.BLACK, background_color: Color = None):
        """
        Draws text on this image.

        The most recent font set using set_font() will be used or Font.DEFAULT if no font has been set yet.

        Args:
            x (int): The x-axis value where the left side of the text will start.
            y (int): The y-axis value where the top of the text will start.
            text (str): The text to draw.
            text_color (Color): The color used for drawing the text.
            background_color (Color): The color used to fill the rectangle behind the text or None for transparent background.
        """
        ...

    def print(self, *args, sep: str = "", end: str = "\n"):
        """
        Prints a line of text on this image.

        This method works like the builtin print() function, but it writes on this image instead.

        You can set the font using set_font(). If no font has been set, Font.DEFAULT will be used. The text is always printed used black text with a white background.

        Unlike the builtin print(), the text does not wrap if it is too wide to fit on this image. It just gets cut off. But if the text would go off of the bottom of this image, the entire image is scrolled up and the text is printed in the new blank area at the bottom of this image.

        Args:
            args (object): Zero or more objects to print.
            sep (str): Separator that will be placed between each object that is printed.
            end (str): End of line that will be printed after the last object.
        """
        ...

    def set_font(self, font: Font):
        """
        Sets the font used for writing on this image.

        The font is used for both draw_text() and print().

        Args:
            font (Font): The font to use.
        """
        ...

    def draw_image(self, x: int, y: int, source: Union[str, 'Image', ImageFile], transparent: Color = None):
        """
        Draws the source image on this image.

        Args:
            x (int): The x-axis value where the left side of the image will start.
            y (int): The y-axis value where the top of the image will start.
            source (Image, ImageFile, or str): The source Image. If the argument is a string, then the source image is loaded from file.
            transparent (Color): The color of image to treat as transparent or None for no transparency.
        """
        ...

    def draw_pixel(self, x: int, y: int, color: Color = Color.BLACK):
        """
        Draws a single pixel on this image.

        Args:
            x (int): The x coordinate of the pixel.
            y (int): The y coordinate of the pixel.
            color (Color): The color of the pixel.
        """
        ...

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 1, color: Color = Color.BLACK):
        """
        Draws a line on this image.

        Args:
            x1 (int): The x coordinate of the starting point of the line.
            y1 (int): The y coordinate of the starting point of the line.
            x2 (int): The x coordinate of the ending point of the line.
            y2 (int): The y coordinate of the ending point of the line.
            width (int): The width of the line in pixels.
            color (Color): The color of the line.
        """
        ...

    def draw_box(self, x1: int, y1: int, x2: int, y2: int, r: int = 0, fill: bool = False, color: Color = Color.BLACK):
        """
        Draws a box on this image.

        Args:
            x1 (int): The x coordinate of the left side of the box.
            y1 (int): The y coordinate of the top of the box.
            x2 (int): The x coordinate of the right side of the box.
            y2 (int): The y coordinate of the bottom of the box.
            r (int): The radius of the corners of the box.
            fill (bool): If True, the box will be filled with color, otherwise only the outline of the box will be drawn.
            color (Color): The color of the box.
        """
        ...

    def draw_circle(self, x: int, y: int, r: int, fill: bool = False, color: Color = Color.BLACK):
        """
        Draws a circle on this image.

        Args:
            x (int): The x coordinate of the center of the circle.
            y (int): The y coordinate of the center of the circle.
            r (int): The radius of the circle.
            fill (bool): If True, the circle will be filled with color, otherwise only the circumference will be drawn.
            color (Color): The color of the circle.
        """
        ...

    def clear(self):
        """
        Clears this image. All pixels on this image will be set to Color.WHITE.
        """
        ...

    def load_image(self, source: Union['Image', str, ImageFile]):
        """
        Clears this image, then draws the source image centered in this image.

        Args:
            source (Image or str): The source Image. If the argument is a string, then the source image is loaded from file.
        """
        ...

    def save(self, filename: str):
        """
        Saves this image as a .png file.

        Args:
            filename (str): The path to the file to be saved.

        Raises:
            TypeError: filename is not a string.
            OSError: There was a problem saving the file.
        """
        ...

empty = Image('empty')