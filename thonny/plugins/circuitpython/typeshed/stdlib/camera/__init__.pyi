"""Support for camera input

The `camera` module contains classes to control the camera and take pictures."""

from __future__ import annotations

from circuitpython_typing import WriteableBuffer

class Camera:
    """The class to control camera.

    Usage::

        import board
        import sdioio
        import storage
        import camera

        sd = sdioio.SDCard(
            clock=board.SDIO_CLOCK,
            command=board.SDIO_COMMAND,
            data=board.SDIO_DATA,
            frequency=25000000)
        vfs = storage.VfsFat(sd)
        storage.mount(vfs, '/sd')

        cam = camera.Camera()

        buffer = bytearray(512 * 1024)
        file = open("/sd/image.jpg","wb")
        size = cam.take_picture(buffer, width=1920, height=1080, format=camera.ImageFormat.JPG)
        file.write(buffer, size)
        file.close()"""

    def __init__(self) -> None:
        """Initialize camera."""
        ...

    def deinit(self) -> None:
        """De-initialize camera."""
        ...

    def take_picture(self, buf: WriteableBuffer, format: ImageFormat) -> int:
        """Take picture and save to ``buf`` in the given ``format``. The size of the picture
        taken is ``width`` by ``height`` in pixels.

        :return: the number of bytes written into buf
        :rtype: int"""
        ...

class ImageFormat:
    """Image format"""

    def __init__(self) -> None:
        """Enum-like class to define the image format."""
    JPG: ImageFormat
    """JPG format."""

    RGB565: ImageFormat
    """RGB565 format."""
