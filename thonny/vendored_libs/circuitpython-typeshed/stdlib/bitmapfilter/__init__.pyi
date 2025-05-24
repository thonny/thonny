from __future__ import annotations

from typing import Callable, Sequence, Tuple

import displayio

def morph(
    bitmap: displayio.Bitmap,
    weights: Sequence[int],
    mul: float | None = None,
    add: float = 0,
    mask: displayio.Bitmap | None = None,
    threshold: bool = False,
    offset: int = 0,
    invert: bool = False,
) -> displayio.Bitmap:
    """Convolve an image with a kernel

    The name of the function comes from
    `OpenMV <https://docs.openmv.io/library/omv.image.html#image.Image.morph>`_.
    ImageMagick calls this "-morphology" ("-morph" is an unrelated image blending
    algorithm). PIL calls this "kernel".

    For background on how this kind of image processing, including some
    useful ``weights`` values, see `wikipedia's article on the
    subject <https://en.wikipedia.org/wiki/Kernel_(image_processing)>`_.

    The ``bitmap``, which must be in RGB565_SWAPPED format, is modified
    according to the ``weights``. Then a scaling factor ``mul`` and an
    offset factor ``add`` are applied.

    The ``weights`` must be a sequence of integers. The length of the tuple
    must be the square of an odd number, usually 9 and sometimes 25.
    Specific weights create different effects. For instance, these
    weights represent a 3x3 gaussian blur: ``[1, 2, 1, 2, 4, 2, 1, 2, 1]``

    ``mul`` is number to multiply the convolution pixel results by.
    If `None` (the default) is passed, the value of ``1/sum(weights)``
    is used (or ``1`` if ``sum(weights)`` is ``0``). For most weights, his
    default value will preserve the overall image brightness.

    ``add`` is a value to add to each convolution pixel result.

    ``mul`` basically allows you to do a global contrast adjustment and
    add allows you to do a global brightness adjustment. Pixels that go
    outside of the image mins and maxes for color channels will be
    clipped.

    If you’d like to adaptive threshold the image on the output of the
    filter you can pass ``threshold=True`` which will enable adaptive
    thresholding of the image which sets pixels to one or zero based on a
    pixel’s brightness in relation to the brightness of the kernel of pixels
    around them. A negative ``offset`` value sets more pixels to 1 as you make
    it more negative while a positive value only sets the sharpest contrast
    changes to 1. Set ``invert`` to invert the binary image resulting output.

    ``mask`` is another image to use as a pixel level mask for the operation.
    The mask should be an image the same size as the image being operated on.
    Only pixels set to a non-zero value in the mask are modified.

    .. code-block:: python

        kernel_gauss_3 = [
            1, 2, 1,
            2, 4, 2,
            1, 2, 1]

        def blur(bitmap):
            \"""Blur the bitmap with a 3x3 gaussian kernel\"""
            bitmapfilter.morph(bitmap, kernel_gauss_3, 1/sum(kernel_gauss_3))
    """

class ChannelScale:
    """A weight object to use with mix() that scales each channel independently

    This is useful for global contrast and brightness adjustment on a
    per-component basis. For instance, to cut red contrast in half (while keeping the minimum value
    as black or 0.0),

    .. code-block:: python

        reduce_red_contrast = bitmapfilter.ChannelScale(0.5, 1, 1)
    """

    def __init__(self, r: float, g: float, b: float) -> None:
        """Construct a ChannelScale object

        The ``r`` parameter gives the scale factor for the red channel of
        pixels, and so forth."""

class ChannelScaleOffset:
    """A weight object to use with mix() that scales and offsets each channel independently

    The ``r``, ``g``, and ``b`` parameters give a scale factor for each color
    component, while the ``r_add`, ``g_add`` and ``b_add`` give offset values
    added to each component.

    This is useful for global contrast and brightness adjustment on a
    per-component basis. For instance, to cut red contrast in half while adjusting the
    brightness so that the middle value is still 0.5:

    .. code-block:: python

        reduce_red_contrast = bitmapfilter.ChannelScaleOffset(
                0.5, 0.25,
                1, 0,
                1, 0)
    """

    def __init__(
        self, r: float, r_add: float, g: float, g_add: float, b: float, b_add: float
    ) -> None:
        """Construct a ChannelScaleOffset object"""

class ChannelMixer:
    """A weight object to use with mix() that mixes different channels together

    The parameters with names like ``rb`` give the fraction of
    each channel to mix into every other channel. For instance,
    ``rb`` gives the fraction of blue to mix into red, and ``gg``
    gives the fraction of green to mix into green.

    Conversion to sepia is an example where a ChannelMixer is appropriate,
    because the sepia conversion is defined as mixing a certain fraction of R,
    G, and B input values into each output value:

    .. code-block:: python

        sepia_weights = bitmapfilter.ChannelMixer(
            .393,  .769,   .189,
            .349,  .686,   .168,
            .272,  .534,   .131)

        def sepia(bitmap):
            \"""Convert the bitmap to sepia\"""
            bitmapfilter.mix(bitmap, sepia_weights)
        mix_into_red = ChannelMixer(
                0.5, 0.25, 0.25,
                0,   1,    0,
                0,   1,    0)
    """

    def __init__(
        self,
        rr: float,
        rg: float,
        rb: float,
        gr: float,
        gg: float,
        gb: float,
        br: float,
        bg: float,
        bb: float,
    ) -> None:
        """Construct a ChannelMixer object"""

class ChannelMixerOffset:
    """A weight object to use with mix() that mixes different channels together, plus an offset value

    The parameters with names like ``rb`` give the fraction of
    each channel to mix into every other channel. For instance,
    ``rb`` gives the fraction of blue to mix into red, and ``gg``
    gives the fraction of green to mix into green.  The ``r_add``, ``g_add``
    and ``b_add`` parameters give offsets applied to each component.

    For instance, to perform sepia conversion but also increase the overall brightness by 10%:

    .. code-block:: python

        sepia_weights_brighten = bitmapfilter.ChannelMixerOffset(
            .393,  .769,   .189, .1
            .349,  .686,   .168, .1
            .272,  .534,   .131, .1)
    """

    def __init__(
        self,
        rr: float,
        rg: float,
        rb: float,
        r_add: float,
        gr: float,
        gg: float,
        gb: float,
        g_add: float,
        br: float,
        bg: float,
        bb: float,
        b_add: float,
    ) -> None:
        """Construct a ChannelMixerOffset object"""

def mix(
    bitmap: displayio.Bitmap,
    weights: ChannelScale | ChannelScaleOffset | ChannelMixer | ChannelMixerOffset,
    mask: displayio.Bitmap | None = None,
) -> displayio.Bitmap:
    """Perform a channel mixing operation on the bitmap

    This is similar to the "channel mixer" tool in popular photo editing software.
    Imagemagick calls this "-color-matrix". In PIL, this is accomplished with the
    ``convert`` method's ``matrix`` argument.

    The ``bitmap``, which must be in RGB565_SWAPPED format, is modified
    according to the ``weights``.

    The ``weights`` must be one of the above types: `ChannelScale`,
    `ChannelScaleOffset`, `ChannelMixer`, or `ChannelMixerOffset`. For the
    effect of each different kind of weights object, see the type
    documentation.

    After computation, any out of range values are clamped to the greatest or
    smallest valid value.

    ``mask`` is another image to use as a pixel level mask for the operation.
    The mask should be an image the same size as the image being operated on.
    Only pixels set to a non-zero value in the mask are modified.
    """

def solarize(
    bitmap: displayio.Bitmap,
    threshold: float = 0.5,
    mask: displayio.Bitmap | None = None,
) -> displayio.Bitmap:
    """Create a "solarization" effect on an image

    This filter inverts pixels with brightness values above ``threshold``, while leaving
    lower brightness pixels alone.

    This effect is similar to `an effect observed in real life film
    <https://en.wikipedia.org/wiki/Solarization_(photography)>`_ which can also be
    `produced during the printmaking process
    <https://en.wikipedia.org/wiki/Sabattier_effect>`_

    PIL and ImageMagic both call this "solarize".
    """

LookupFunction = Callable[[float], float]
"""Any function which takes a number and returns a number. The input
and output values should be in the range from 0 to 1 inclusive."""
ThreeLookupFunctions = Tuple[LookupFunction, LookupFunction, LookupFunction]
"""Any sequenceof three `LookupFunction` objects"""

def lookup(
    bitmap: displayio.Bitmap,
    lookup: LookupFunction | ThreeLookupFunctions,
    mask: displayio.Bitmap | None,
) -> displayio.Bitmap:
    """Modify the channels of a bitmap according to a look-up table

    This can be used to implement non-linear transformations of color values,
    such as gamma curves.

    This is similar to, but more limiting than, PIL's "LUT3D" facility. It is not
    directly available in OpenMV or ImageMagic.

    The ``bitmap``, which must be in RGB565_SWAPPED format, is modified
    according to the values of the ``lookup`` function or functions.

    If one ``lookup`` function is supplied, the same function is used for all 3
    image channels. Otherwise, it must be a tuple of 3 functions. The first
    function is used for R, the second function for G, and the third for B.

    Each lookup function is called for each possible channel value from 0 to 1
    inclusive (64 times for green, 32 times for red or blue), and the return
    value (also from 0 to 1) is used whenever that color value is returned.

    ``mask`` is another image to use as a pixel level mask for the operation.
    The mask should be an image the same size as the image being operated on.
    Only pixels set to a non-zero value in the mask are modified.
    """

def false_color(
    bitmap: displayio.Bitmap,
    palette: displayio.Palette,
    mask: displayio.Bitmap | None,
) -> displayio.Bitmap:
    """Convert the image to false color using the given palette

    In OpenMV this is accomplished via the ``ironbow`` function, which uses a default
    palette known as "ironbow". Imagemagic produces a similar effect with ``-clut``.
    PIL can accomplish this by converting an image to "L" format, then applying a
    palette to convert it into "P" mode.

    The ``bitmap``, which must be in RGB565_SWAPPED format, is converted into false color.

    The ``palette``, which must be of length 256, is used as a look-up table.

    Each pixel is converted to a luminance (brightness/greyscale) value
    in the range 0..255, then the corresponding palette entry is looked up and
    stored in the bitmap.

    ``mask`` is another image to use as a pixel level mask for the operation.
    The mask should be an image the same size as the image being operated on.
    Only pixels set to a non-zero value in the mask are modified.
    """

BlendFunction = Callable[[float, float], float]
"""A function used to blend two images"""

BlendTable = bytearray
"""A precomputed blend table

There is not actually a BlendTable type. The real type is actually any
buffer 4096 bytes in length."""

def blend_precompute(
    lookup: BlendFunction, table: BlendTable | None = None
) -> BlendTable:
    """Precompute a BlendTable from a BlendFunction

    If the optional ``table`` argument is provided, an existing `BlendTable` is updated
    with the new function values.

    The function's two arguments will range from 0 to 1. The returned value should also range from 0 to 1.

    A function to do a 33% blend of each source image could look like this:

    .. code-block:: python

        def blend_one_third(a, b):
            return a * .33 + b * .67
    """

def blend(
    dest: displayio.Bitmap,
    src1: displayio.Bitmap,
    src2: displayio.Bitmap,
    lookup: BlendFunction | BlendTable,
    mask: displayio.Bitmap | None = None,
) -> displayio.Bitmap:
    """Blend the 'src1' and 'src2' images according to lookup function or table 'lookup'

    If ``lookup`` is a function, it is converted to a `BlendTable` by
    internally calling blend_precompute. If a blend function is used repeatedly
    it can be more efficient to compute it once with `blend_precompute`.

    If the mask is supplied, pixels from ``src1`` are taken unchanged in masked areas.

    The source and destination bitmaps may be the same bitmap.

    The destination bitmap is returned.
    """
