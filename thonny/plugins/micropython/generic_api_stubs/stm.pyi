"""
functionality specific to STM32 MCUs.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/stm.rst.
===================================================

.. module:: stm
    :synopsis: functionality specific to STM32 MCUs

This module provides functionality specific to STM32 microcontrollers, including
direct access to peripheral registers.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final

# noinspection PyPep8Naming
class mem:
    """
    Memory objects that can be used in combination with the peripheral register
    constants to read and write registers of the MCU hardware peripherals, as well
    as all other areas of address space.
    
    Cannot make an instance of this class,
    but pre-made instances: `mem8`, `mem16`, and `mem32` are available for 8, 16, and 32 bit access respectively.
    """

    def __getitem__(self, loc: int, /) -> int:
        """
        Get the contents of the given memory location using subscript notation e.g., `mem8[0]`.
        Returns 8 bits for mem8`, 16 bits for `mem16`, and 32 bits for `mem32`, in all cases as a single `int`.
        Location doesn't overflow, it is truncated.
        
        Can be used in combination with the peripheral register
        constants to read registers of the MCU hardware peripherals, as well
        as all other areas of address space.
        """
    def __setitem__(self, loc: int, value: int, /) -> None:
        """
        Set the contents of the given memory location to the given value using subscript notation e.g., `mem8[0] = 195`.
        Sets 8 bits for `mem8`, 16 bits for `mem16`, and 32 bits for `mem32`, from the given `int` value.
        Location doesn't overflow, it is truncated.
        
        Can be used in combination with the peripheral register
        constants to write registers of the MCU hardware peripherals, as well
        as all other areas of address space.
        """

mem8: Final[mem] = ...
"""
Read/write 8 bits of memory.
"""

mem16: Final[mem] = ...
"""
Read/write 16 bits of memory.
"""

mem32: Final[mem] = ...
"""
Read/write 32 bits of memory.
"""

GPIOA: Final[int] = ...
"""
Base address of the GPIOA peripheral.

The module defines constants for registers which are generated from CMSIS header
files, and the constants available depend on the microcontroller series that is
being compiled for.  Examples of some constants include:
address of that peripheral.  Constants that have a prefix which is the name of a
peripheral, like ``GPIO_BSRR``, are relative offsets of the register.  Accessing
peripheral registers requires adding the absolute base address of the peripheral
and the relative register offset.  For example ``GPIOA + GPIO_BSRR`` is the
full, absolute address of the ``GPIOA->BSRR`` register.

Example use:

.. code-block:: python3

    # set PA2 high
    stm.mem32[stm.GPIOA + stm.GPIO_BSRR] = 1 << 2

    # read PA3
    value = (stm.mem32[stm.GPIOA + stm.GPIO_IDR] >> 3) & 1
"""

GPIOB: Final[int] = ...
"""
Base address of the GPIOB peripheral.

The module defines constants for registers which are generated from CMSIS header
files, and the constants available depend on the microcontroller series that is
being compiled for.  Examples of some constants include:
address of that peripheral.  Constants that have a prefix which is the name of a
peripheral, like ``GPIO_BSRR``, are relative offsets of the register.  Accessing
peripheral registers requires adding the absolute base address of the peripheral
and the relative register offset.  For example ``GPIOA + GPIO_BSRR`` is the
full, absolute address of the ``GPIOA->BSRR`` register.

Example use:

.. code-block:: python3

    # set PA2 high
    stm.mem32[stm.GPIOA + stm.GPIO_BSRR] = 1 << 2

    # read PA3
    value = (stm.mem32[stm.GPIOA + stm.GPIO_IDR] >> 3) & 1
"""

GPIO_BSRR: Final[int] = ...
"""
Offset of the GPIO bit set/reset register.

The module defines constants for registers which are generated from CMSIS header
files, and the constants available depend on the microcontroller series that is
being compiled for.  Examples of some constants include:
address of that peripheral.  Constants that have a prefix which is the name of a
peripheral, like ``GPIO_BSRR``, are relative offsets of the register.  Accessing
peripheral registers requires adding the absolute base address of the peripheral
and the relative register offset.  For example ``GPIOA + GPIO_BSRR`` is the
full, absolute address of the ``GPIOA->BSRR`` register.

Example use:

.. code-block:: python3

    # set PA2 high
    stm.mem32[stm.GPIOA + stm.GPIO_BSRR] = 1 << 2

    # read PA3
    value = (stm.mem32[stm.GPIOA + stm.GPIO_IDR] >> 3) & 1
"""

GPIO_IDR: Final[int] = ...
"""
Offset of the GPIO input data register.

The module defines constants for registers which are generated from CMSIS header
files, and the constants available depend on the microcontroller series that is
being compiled for.  Examples of some constants include:
address of that peripheral.  Constants that have a prefix which is the name of a
peripheral, like ``GPIO_BSRR``, are relative offsets of the register.  Accessing
peripheral registers requires adding the absolute base address of the peripheral
and the relative register offset.  For example ``GPIOA + GPIO_BSRR`` is the
full, absolute address of the ``GPIOA->BSRR`` register.

Example use:

.. code-block:: python3

    # set PA2 high
    stm.mem32[stm.GPIOA + stm.GPIO_BSRR] = 1 << 2

    # read PA3
    value = (stm.mem32[stm.GPIOA + stm.GPIO_IDR] >> 3) & 1
"""

GPIO_ODR: Final[int] = ...
"""
Offset of the GPIO output data register.

Constants that are named after a peripheral, like ``GPIOA``, are the absolute
The module defines constants for registers which are generated from CMSIS header
files, and the constants available depend on the microcontroller series that is
being compiled for.  Examples of some constants include:
address of that peripheral.  Constants that have a prefix which is the name of a
peripheral, like ``GPIO_BSRR``, are relative offsets of the register.  Accessing
peripheral registers requires adding the absolute base address of the peripheral
and the relative register offset.  For example ``GPIOA + GPIO_BSRR`` is the
full, absolute address of the ``GPIOA->BSRR`` register.

Example use:

.. code-block:: python3

    # set PA2 high
    stm.mem32[stm.GPIOA + stm.GPIO_BSRR] = 1 << 2

    # read PA3
    value = (stm.mem32[stm.GPIOA + stm.GPIO_IDR] >> 3) & 1
"""

def rfcore_status() -> int:
    """
    Returns the status of the second CPU as an integer (the first word of device
    info table).
    
    These functions are available on STM32WBxx microcontrollers, and interact with
    the second CPU, the RF core.
   """

def rfcore_fw_version(id: int, /) -> tuple[int, int, int, int, int]:
    """
    Get the version of the firmware running on the second CPU.  Pass in 0 for
    *id* to get the FUS version, and 1 to get the WS version.
    
    Returns a 5-tuple with the full version number.
    
    These functions are available on STM32WBxx microcontrollers, and interact with
    the second CPU, the RF core.
   """

def rfcore_sys_hci(ogf: int, ocf: int, data: int, timeout_ms: int = 0, /) -> bytes:
    """
    Execute a HCI command on the SYS channel.  The execution is synchronous.
    
    Returns a bytes object with the result of the SYS command.
    These functions are available on STM32WBxx microcontrollers, and interact with
    the second CPU, the RF core.
   """
