class BluetoothMailboxClient:
    """
    Object that represents a Bluetooth connection to one or more remote EV3s.

    The remote EV3s can either be running MicroPython or the standard EV3 firmware.

    A “client” initiates a connection to a waiting “server”.
    """

    def __init__(self):
        ...

    def connect(self, brick: str):
        """
        Connects to a BluetoothMailboxServer on another device.

        The remote device must be paired and waiting for a connection. See BluetoothMailboxServer.wait_for_connection().

        Args:
            brick (str): The name or Bluetooth address of the remove EV3 to connect to.

        Raises:
            OSError: There was a problem establishing the connection.
        """
        ...

    def close(self):
        """
        Closes all connections.
        """
        ...
