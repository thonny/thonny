class LogicMailbox:
    """
    Object that represents a mailbox containing boolean data.

    This works just like a regular Mailbox, but values must be True or False.

    This is compatible with the “logic” mailbox type in EV3-G.

    Args:
        name (str): The name of this mailbox.
        connection: A connection object such as BluetoothMailboxClient.
    """

    def __init__(self, name: str, connection: object):
        ...

    def read(self) -> bool:
        """
        Gets the current value of the mailbox.

        Returns:
            The current value or None if the mailbox is empty.
        """
        return False

    def send(self, value: bool, brick: str):
        """
        Sends a value to this mailbox on connected devices.

        Args:
            value (bool): The value that will be delivered to the mailbox.
            brick (str): The name or Bluetooth address of the brick or None to broadcast to all connected devices.

        Raises:
            OSError: There is a problem with the connection.
        """
        ...

    def wait_new(self) -> bool:
        """
        Waits for a new value to be delivered to the mailbox that is not equal to the current value in the mailbox.

        Returns:
            The new value.
        """
        return False

    def wait(self):
        """
        Waits for the mailbox to be updated by remote device.
        """
        ...
