"""Routines for low-level manipulation of binary data"""

from __future__ import annotations

from circuitpython_typing import ReadableBuffer, WriteableBuffer

def bit_transpose(
    input: ReadableBuffer, output: WriteableBuffer, width: int = 8
) -> WriteableBuffer:
    """ "Transpose" a buffer by assembling each output byte with bits taken from each of ``width`` different input bytes.

    This can be useful to convert a sequence of pixel values into a single
    stream of bytes suitable for sending via a parallel conversion method.

    The number of bytes in the input buffer must be a multiple of the width,
    and the width can be any value from 2 to 8.  If the width is fewer than 8,
    then the remaining (less significant) bits of the output are set to zero.

    Let ``stride = len(input)//width``.  Then the first byte is made out of the
    most significant bits of ``[input[0], input[stride], input[2*stride], ...]``.
    The second byte is made out of the second bits, and so on until the 8th output
    byte which is made of the first bits of ``input[1], input[1+stride,
    input[2*stride], ...]``.

    The required output buffer size is ``len(input) * 8  // width``.

    Returns the output buffer."""
    ...
