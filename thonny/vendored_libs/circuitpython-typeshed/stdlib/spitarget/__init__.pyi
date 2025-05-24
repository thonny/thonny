"""Serial Peripheral Interface protocol target

The `spitarget` module contains classes to support an SPI target.

Example that emulates an SPI analog-to-digital converter::

  import board
  import analogio
  from spitarget import SPITarget

  ain0 = analogio.AnalogIn(board.A0)
  ain1 = analogio.AnalogIn(board.A1)
  selected_channel = ain0

  def map_adc_channel(index):
      return ain0 if (index == 0) else ain1

  mosi_buffer = bytearray(2)
  miso_buffer = bytearray(2)
  with SPITarget(sck=board.D12, mosi=board.D13, miso=board.D11, ss=board.D10) as device:
      while True:
          # Convert analog signal to array of bytes
          reading = selected_channel.value
          miso_buffer[0] = (reading >> 8) & 0xFF
          miso_buffer[1] = (reading) & 0xFF
          # Send array of bytes over SPI to main
          device.load_packet(mosi_buffer, miso_buffer)
          while not device.wait_transfer(timeout=-1):
              pass
          # Handle command from main, which sets the ADC channel
          selected_channel = map_adc_channel((mosi_buffer[0] << 8) | mosi_buffer[1])

Communicating with the ADC emulator from the REPL of an attached CircuitPython board might look like ::

  >>> import board
  >>> import digitalio
  >>> import busio
  >>> import time
  >>>
  >>> ## setup
  >>> spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
  >>> cs = digitalio.DigitalInOut(board.CS)
  >>> cs.direction = digitalio.Direction.OUTPUT
  >>> cs.value = True
  >>> spi.try_lock()
  True
  >>>
  >>> ## ADC command: read from A0
  >>> cs.value = False
  >>> spi.write(bytearray([0, 0]))
  >>> cs.value = True
  >>>
  >>> # wait for ADC to read a value
  >>>
  >>> ## get two-byte output from ADC
  >>> adc_result = bytearray(2)
  >>> cs.value = False
  >>> spi.readinto(adc_result, write_value=1)
  >>> cs.value = True
  >>> list(adc_result)
  [0, 255]

"""

from __future__ import annotations

import microcontroller

class SPITarget:
    """Serial Peripheral Interface protocol target"""

    def __init__(
        self,
        sck: microcontroller.Pin,
        mosi: microcontroller.Pin,
        miso: microcontroller.Pin,
        ss: microcontroller.Pin,
    ) -> None:
        """SPI is a four-wire protocol for communicating between devices.
        This implements the secondary (aka target or peripheral) side.

        :param ~microcontroller.Pin sck: The SPI clock pin
        :param ~microcontroller.Pin mosi: The pin transferring data from the main to the secondary
        :param ~microcontroller.Pin miso: The pin transferring data from the secondary to the main
        :param ~microcontroller.Pin ss: The secondary selection pin"""
        ...

    def deinit(self) -> None:
        """Releases control of the underlying hardware so other classes can use it."""
        ...

    def __enter__(self) -> SPITarget:
        """No-op used in Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware on context exit. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def load_packet(self, mosi_packet: bytearray, miso_packet: bytearray) -> None:
        """Queue data for the next SPI transfer from the main device.
        If a packet has already been queued for this SPI bus but has not yet been transferred, an error will be raised.

        :param bytearray miso_packet: Packet data to be sent from secondary to main on next request.
        :param bytearray mosi_packet: Packet to be filled with data from main on next request.
        """

    def wait_transfer(self, *, timeout: float = -1) -> bool:
        """Wait for an SPI transfer from the main device.

        :param float timeout: Timeout in seconds. Zero means wait forever, a negative value means check once
        :return: True if the transfer is complete, or False if no response received before the timeout
        """
