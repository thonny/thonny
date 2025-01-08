"""Low-level BridgeTek EVE bindings

The `_eve` module provides a class _EVE which
contains methods for constructing EVE command
buffers and appending basic graphics commands."""

from __future__ import annotations

from typing import Tuple

from circuitpython_typing import ReadableBuffer

class _EVE:
    def __init__(self) -> None:
        """Create an _EVE object"""

    def register(self, o: object) -> None: ...
    def setmodel(self, m: int) -> None: ...
    def flush(self) -> None:
        """Send any queued drawing commands directly to the hardware.

        :param int width: The width of the grid in tiles, or 1 for sprites."""
        ...

    def cc(self, b: ReadableBuffer) -> None:
        """Append bytes to the command FIFO.

        :param ~circuitpython_typing.ReadableBuffer b: The bytes to add"""
        ...

    def AlphaFunc(self, func: int, ref: int) -> None:
        """Set the alpha test function

        :param int func: specifies the test function, one of ``NEVER``, ``LESS``, ``LEQUAL``, ``GREATER``, ``GEQUAL``, ``EQUAL``, ``NOTEQUAL``, or ``ALWAYS``. Range 0-7. The initial value is ALWAYS(7)
        :param int ref: specifies the reference value for the alpha test. Range 0-255. The initial value is 0

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Begin(self, prim: int) -> None:
        """Begin drawing a graphics primitive

        :param int prim: graphics primitive.

        Valid primitives are ``BITMAPS``, ``POINTS``, ``LINES``, ``LINE_STRIP``, ``EDGE_STRIP_R``, ``EDGE_STRIP_L``, ``EDGE_STRIP_A``, ``EDGE_STRIP_B`` and ``RECTS``.
        """
        ...

    def BitmapExtFormat(self, format: int) -> None:
        """Set the bitmap format

        :param int format: bitmap pixel format."""
        ...

    def BitmapHandle(self, handle: int) -> None:
        """Set the bitmap handle

        :param int handle: bitmap handle. Range 0-31. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapLayoutH(self, linestride: int, height: int) -> None:
        """Set the source bitmap memory format and layout for the current handle. high bits for large bitmaps

        :param int linestride: high part of bitmap line stride, in bytes. Range 0-7
        :param int height: high part of bitmap height, in lines. Range 0-3"""
        ...

    def BitmapLayout(self, format: int, linestride: int, height: int) -> None:
        """Set the source bitmap memory format and layout for the current handle

        :param int format: bitmap pixel format, or GLFORMAT to use BITMAP_EXT_FORMAT instead. Range 0-31
        :param int linestride: bitmap line stride, in bytes. Range 0-1023
        :param int height: bitmap height, in lines. Range 0-511"""
        ...

    def BitmapSizeH(self, width: int, height: int) -> None:
        """Set the screen drawing of bitmaps for the current handle. high bits for large bitmaps

        :param int width: high part of drawn bitmap width, in pixels. Range 0-3
        :param int height: high part of drawn bitmap height, in pixels. Range 0-3"""
        ...

    def BitmapSize(
        self, filter: int, wrapx: int, wrapy: int, width: int, height: int
    ) -> None:
        """Set the screen drawing of bitmaps for the current handle

        :param int filter: bitmap filtering mode, one of ``NEAREST`` or ``BILINEAR``. Range 0-1
        :param int wrapx: bitmap :math:`x` wrap mode, one of ``REPEAT`` or ``BORDER``. Range 0-1
        :param int wrapy: bitmap :math:`y` wrap mode, one of ``REPEAT`` or ``BORDER``. Range 0-1
        :param int width: drawn bitmap width, in pixels. Range 0-511
        :param int height: drawn bitmap height, in pixels. Range 0-511"""
        ...

    def BitmapSource(self, addr: int) -> None:
        """Set the source address for bitmap graphics

        :param int addr: Bitmap start address, pixel-aligned, low part.
        """
        ...

    def BitmapSourceH(self, addr: int) -> None:
        """Set the high source address for bitmap graphics

        :param int addr: Bitmap start address, pixel-aligned, high part.
        """
        ...

    def BitmapSwizzle(self, r: int, g: int, b: int, a: int) -> None:
        """Set the source for the r,g,b and a channels of a bitmap

        :param int r: red component source channel. Range 0-7
        :param int g: green component source channel. Range 0-7
        :param int b: blue component source channel. Range 0-7
        :param int a: alpha component source channel. Range 0-7"""
        ...

    def BitmapTransformA(self, v: float) -> None:
        """Set the :math:`a` component of the bitmap transform matrix

        :param float v: The :math:`a` component of the bitmap transform matrix

        The initial value 1.0.

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapTransformB(self, v: float) -> None:
        """Set the :math:`b` component of the bitmap transform matrix

        :param float v: The :math:`b` component of the bitmap transform matrix

        The initial value 0.0.

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapTransformC(self, v: float) -> None:
        """Set the :math:`c` component of the bitmap transform matrix

        :param int v: The :math:`c` component of the bitmap transform matrix

        The initial value 0.0.

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapTransformD(self, v: float) -> None:
        """Set the :math:`d` component of the bitmap transform matrix

        :param float v: The :math:`d` component of the bitmap transform matrix

        The initial value 0.0.

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapTransformE(self, v: float) -> None:
        """Set the :math:`e` component of the bitmap transform matrix

        :param float v: The :math:`e` component of the bitmap transform matrix

        The initial value 1.0.

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BitmapTransformF(self, v: int) -> None:
        """Set the :math:`f` component of the bitmap transform matrix

        :param int v: The :math:`f` component of the bitmap transform matrix

        The initial value 0.0.

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def BlendFunc(self, src: int, dst: int) -> None:
        """Set pixel arithmetic

        :param int src: specifies how the source blending factor is computed.  One of ``ZERO``, ``ONE``, ``SRC_ALPHA``, ``DST_ALPHA``, ``ONE_MINUS_SRC_ALPHA`` or ``ONE_MINUS_DST_ALPHA``. Range 0-7. The initial value is SRC_ALPHA(2)
        :param int dst: specifies how the destination blending factor is computed, one of the same constants as **src**. Range 0-7. The initial value is ONE_MINUS_SRC_ALPHA(4)

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Call(self, dest: int) -> None:
        """Execute a sequence of commands at another location in the display list

        :param int dest: display list address. Range 0-65535"""
        ...

    def Cell(self, cell: int) -> None:
        """Set the bitmap cell number for the vertex2f command

        :param int cell: bitmap cell number. Range 0-127. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ClearColorA(self, alpha: int) -> None:
        """Set clear value for the alpha channel

        :param int alpha: alpha value used when the color buffer is cleared. Range 0-255. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ClearColorRGB(self, red: int, green: int, blue: int) -> None:
        """Set clear values for red, green and blue channels

        :param int red: red value used when the color buffer is cleared. Range 0-255. The initial value is 0
        :param int green: green value used when the color buffer is cleared. Range 0-255. The initial value is 0
        :param int blue: blue value used when the color buffer is cleared. Range 0-255. The initial value is 0

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Clear(self, c: int, s: int, t: int) -> None:
        """Clear buffers to preset values

        :param int c: clear color buffer. Range 0-1
        :param int s: clear stencil buffer. Range 0-1
        :param int t: clear tag buffer. Range 0-1"""
        ...

    def ClearStencil(self, s: int) -> None:
        """Set clear value for the stencil buffer

        :param int s: value used when the stencil buffer is cleared. Range 0-255. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ClearTag(self, s: int) -> None:
        """Set clear value for the tag buffer

        :param int s: value used when the tag buffer is cleared. Range 0-255. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """

    def ColorA(self, alpha: int) -> None:
        """Set the current color alpha

        :param int alpha: alpha for the current color. Range 0-255. The initial value is 255

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ColorMask(self, r: int, g: int, b: int, a: int) -> None:
        """Enable and disable writing of frame buffer color components

        :param int r: allow updates to the frame buffer red component. Range 0-1. The initial value is 1
        :param int g: allow updates to the frame buffer green component. Range 0-1. The initial value is 1
        :param int b: allow updates to the frame buffer blue component. Range 0-1. The initial value is 1
        :param int a: allow updates to the frame buffer alpha component. Range 0-1. The initial value is 1

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ColorRGB(self, red: int, green: int, blue: int) -> None:
        """Set the drawing color

        :param int red: red value for the current color. Range 0-255. The initial value is 255
        :param int green: green for the current color. Range 0-255. The initial value is 255
        :param int blue: blue for the current color. Range 0-255. The initial value is 255

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Display(self) -> None:
        """End the display list"""
        ...

    def End(self) -> None:
        """End drawing a graphics primitive

        :meth:`Vertex2ii` and :meth:`Vertex2f` calls are ignored until the next :meth:`Begin`.
        """
        ...

    def Jump(self, dest: int) -> None:
        """Execute commands at another location in the display list

        :param int dest: display list address. Range 0-65535"""
        ...

    def Macro(self, m: int) -> None:
        """Execute a single command from a macro register

        :param int m: macro register to read. Range 0-1"""
        ...

    def Nop(self) -> None:
        """No operation"""
        ...

    def PaletteSource(self, addr: int) -> None:
        """Set the base address of the palette

        :param int addr: Address in graphics RAM, 2-byte aligned, low part.

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def PaletteSourceH(self, addr: int) -> None:
        """Set the base address of the palette

        :param int addr: Address in graphics RAM, 2-byte aligned, high part.

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def RestoreContext(self) -> None:
        """Restore the current graphics context from the context stack"""
        ...

    def Return(self) -> None:
        """Return from a previous call command"""
        ...

    def SaveContext(self) -> None:
        """Push the current graphics context on the context stack"""
        ...

    def ScissorSize(self, width: int, height: int) -> None:
        """Set the size of the scissor clip rectangle

        :param int width: The width of the scissor clip rectangle, in pixels. Range 0-4095. The initial value is hsize
        :param int height: The height of the scissor clip rectangle, in pixels. Range 0-4095. The initial value is 2048

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def ScissorXY(self, x: int, y: int) -> None:
        """Set the top left corner of the scissor clip rectangle

        :param int x: The :math:`x` coordinate of the scissor clip rectangle, in pixels. Range 0-2047. The initial value is 0
        :param int y: The :math:`y` coordinate of the scissor clip rectangle, in pixels. Range 0-2047. The initial value is 0

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def StencilFunc(self, func: int, ref: int, mask: int) -> None:
        """Set function and reference value for stencil testing

        :param int func: specifies the test function, one of ``NEVER``, ``LESS``, ``LEQUAL``, ``GREATER``, ``GEQUAL``, ``EQUAL``, ``NOTEQUAL``, or ``ALWAYS``. Range 0-7. The initial value is ALWAYS(7)
        :param int ref: specifies the reference value for the stencil test. Range 0-255. The initial value is 0
        :param int mask: specifies a mask that is ANDed with the reference value and the stored stencil value. Range 0-255. The initial value is 255

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def StencilMask(self, mask: int) -> None:
        """Control the writing of individual bits in the stencil planes

        :param int mask: the mask used to enable writing stencil bits. Range 0-255. The initial value is 255

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def StencilOp(self, sfail: int, spass: int) -> None:
        """Set stencil test actions

        :param int sfail: specifies the action to take when the stencil test fails, one of ``KEEP``, ``ZERO``, ``REPLACE``, ``INCR``, ``INCR_WRAP``, ``DECR``, ``DECR_WRAP``, and ``INVERT``. Range 0-7. The initial value is KEEP(1)
        :param int spass: specifies the action to take when the stencil test passes, one of the same constants as **sfail**. Range 0-7. The initial value is KEEP(1)

        These values are part of the graphics context and are saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def TagMask(self, mask: int) -> None:
        """Control the writing of the tag buffer

        :param int mask: allow updates to the tag buffer. Range 0-1. The initial value is 1

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Tag(self, s: int) -> None:
        """Set the current tag value

        :param int s: tag value. Range 0-255. The initial value is 255

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def Vertex2ii(self, x: int, y: int, handle: int, cell: int) -> None:
        """:param int x: x-coordinate in pixels. Range 0-511
        :param int y: y-coordinate in pixels. Range 0-511
        :param int handle: bitmap handle. Range 0-31
        :param int cell: cell number. Range 0-127

        This method is an alternative to :meth:`Vertex2f`."""
        ...

    def Vertex2f(self, b: float) -> None:
        """Draw a point.

        :param float x: pixel x-coordinate
        :param float y: pixel y-coordinate"""
        ...

    def LineWidth(self, width: float) -> None:
        """Set the width of rasterized lines

        :param float width: line width in pixels. Range 0-511. The initial value is 1

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def PointSize(self, size: float) -> None:
        """Set the diameter of rasterized points

        :param float size: point diameter in pixels. Range 0-1023. The initial value is 1

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def VertexTranslateX(self, x: float) -> None:
        """Set the vertex transformation's x translation component

        :param float x: signed x-coordinate in pixels. Range ±4095. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def VertexTranslateY(self, y: float) -> None:
        """Set the vertex transformation's y translation component

        :param float y: signed y-coordinate in pixels. Range ±4095. The initial value is 0

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def VertexFormat(self, frac: int) -> None:
        """Set the precision of vertex2f coordinates

        :param int frac: Number of fractional bits in X,Y coordinates, 0-4. Range 0-7. The initial value is 4

        This value is part of the graphics context and is saved and restored by :meth:`SaveContext` and :meth:`RestoreContext`.
        """
        ...

    def cmd0(self, n: int) -> None:
        """Append the command word n to the FIFO

        :param int n: The command code

        This method is used by the ``eve`` module to efficiently add
        commands to the FIFO."""
        ...

    def cmd(self, n: int, fmt: str, args: Tuple[str, ...]) -> None:
        """Append a command packet to the FIFO.

        :param int n: The command code
        :param str fmt: The command format `struct` layout
        :param args: The command's arguments
        :type args: tuple(str, ...)

        Supported format codes: h, H, i, I.

        This method is used by the ``eve`` module to efficiently add
        commands to the FIFO."""
        ...
