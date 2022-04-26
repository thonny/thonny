class BluetoothMailboxServer:
    """
    Object that represents a Bluetooth connection from one or more remote EV3s.

    The remote EV3s can either be running MicroPython or the standard EV3 firmware.

    A “server” waits for a “client” to connect to it.
    """

    def __init__(self):
        ...

    def wait_for_connection(self, count: int = 1):
        """
        Waits for a BluetoothMailboxClient on a remote device to connect.

        Args:
            count (int): The number of remote connections to wait for.

        Raises:
            OSError: There was a problem establishing the connection.
        """
        ...

    def close(self):
        """
        Closes all connections.
        """
        ...
