from typing import Union


class NumericMailbox:
    """
    Object that represents a mailbox containing numeric data.

    This works just like a regular Mailbox, but values must be a number, such as 15 or 12.345.

    This is compatible with the "numeric" mailbox type in EV3-G.

    Args:
        name (str): The name of this mailbox.
        connection: A connection object such as BluetoothMailboxClient.
    """

    def __init__(self, name: str, connection: object):
        ...

    def read(self) -> Union[int, float]:
        """
        Gets the current value of the mailbox.

        Returns:
            The current value or None if the mailbox is empty.
        """
        return 0

    def send(self, value: Union[int, float], brick: str):
        """
        Sends a value to this mailbox on connected devices.

        Args:
            value (int or float): The value that will be delivered to the mailbox.
            brick (str): The name or Bluetooth address of the brick or None to broadcast to all connected devices.

        Raises:
            OSError: There is a problem with the connection.
        """
        ...

    def wait_new(self) -> Union[int, float]:
        """
        Waits for a new value to be delivered to the mailbox that is not equal to the current value in the mailbox.

        Returns:
            The new value.
        """
        return 0

    def wait(self):
        """
        Waits for the mailbox to be updated by remote device.
        """
        ...
