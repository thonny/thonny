from typing import Callable


class Mailbox:
    """
    Object that represents a mailbox containing data.

    You can read data that is delivered by other EV3 bricks, or send data to other bricks that have the same mailbox.

    By default, the mailbox reads and send only bytes. To send other data, you can provide an encode function that encodes your Python object into bytes, and a decode function to convert bytes back to a Python object.

    Args:
        name (str): The name of this mailbox.
        connection: A connection object such as BluetoothMailboxClient.
        encode (callable): Function that encodes a Python object to bytes.
        decode (callable): Function that creates a new Python object from bytes.
    """

    def __init__(self, name: str, connection: object, encode: Callable = None, decode: Callable = None):
        ...

    def read(self) -> any:
        """
        Gets the current value of the mailbox.

        Returns:
            The current value or None if the mailbox is empty.
        """
        return ''

    def send(self, value: any, brick: str):
        """
        Sends a value to this mailbox on connected devices.

        Args:
            value (any): The value that will be delivered to the mailbox.
            brick (str): The name or Bluetooth address of the brick or None to broadcast to all connected devices.

        Raises:
            OSError: There is a problem with the connection.
        """
        ...

    def wait(self):
        """
        Waits for the mailbox to be updated by remote device.
        """
        ...

    def wait_new(self) -> any:
        """
        Waits for a new value to be delivered to the mailbox that is not equal to the current value in the mailbox.

        Returns:
            The new value.
        """
        return ''
