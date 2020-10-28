"""Board specific pin names

Common container for board base pin names. These will vary from board to
board so don't expect portability when using this module.

.. warning:: The board module varies by board. The APIs documented here may or may not be
             available on a specific board."""
def I2C() -> Any:
    """Returns the `busio.I2C` object for the board designated SDA and SCL pins. It is a singleton."""
    ...

def SPI() -> Any:
    """Returns the `busio.SPI` object for the board designated SCK, MOSI and MISO pins. It is a
    singleton."""
    ...

def UART() -> Any:
    """Returns the `busio.UART` object for the board designated TX and RX pins. It is a singleton.

    The object created uses the default parameter values for `busio.UART`. If you need to set
    parameters that are not changeable after creation, such as ``receiver_buffer_size``,
    do not use `board.UART()`; instead create a `busio.UART` object explicitly with the
    desired parameters."""
    ...

