import queue
from thonny.misc_utils import TimeHelper
from queue import Queue
import re


class MicroPythonConnection:
    """Utility class for using Serial or WebSocket connection
    
    Uses background thread to read from the source as soon as possible
    to avoid loss of data (because buffer overflow or the device discarding 
    unread data).

    Allows writing with delays after each n bytes.
    
    Allows unreading data.    
    """

    def __init__(self):
        self._read_queue = Queue()  # populated by reader thread
        self._read_buffer = bytearray()  # used for unreading and postponing bytes
        self.num_bytes_received = 0
        self._error = None

    def read(self, size, timeout=1):
        if timeout == 0:
            raise TimeoutError()

        timer = TimeHelper(timeout)

        while len(self._read_buffer) < size:
            self._check_for_error()

            try:
                self._read_buffer.extend(self._read_queue.get(True, timer.time_left))
            except queue.Empty:
                raise TimeoutError("Reaction timeout. Bytes read: %s" % self._read_buffer)

        try:
            data = self._read_buffer[:size]
            return data
        finally:
            del self._read_buffer[:size]

    def soft_read_until(self, terminator, timeout=1000000):
        return self.read_until(terminator, timeout, timeout_is_soft=True)

    def read_until(self, terminator, timeout=1000000, timeout_is_soft=False):
        timer = TimeHelper(timeout)

        if isinstance(terminator, str):
            terminator = re.compile(re.escape(terminator))

        match = None
        while True:
            self._check_for_error()

            match = re.search(terminator, self._read_buffer)
            if match:
                break

            try:
                data = self._read_queue.get(True, timer.time_left)
                # print("RR", repr(data), file=sys.stderr)
                assert len(data) > 0
                self._read_buffer.extend(data)
            except queue.Empty:
                if timeout_is_soft:
                    break
                else:
                    raise TimeoutError("Reaction timeout. Bytes read: %s" % self._read_buffer)

        if match:
            size = match.end()
        else:
            assert timeout_is_soft
            size = len(self._read_buffer)

        data = self._read_buffer[:size]
        del self._read_buffer[:size]
        return data

    def _fetch_to_buffer(self):
        while not self._read_queue.empty():
            self._read_buffer.extend(self._read_queue.get(True))

    def peek_incoming(self):
        self._fetch_to_buffer()
        return self._read_buffer

    def read_all(self):
        self._fetch_to_buffer()

        if len(self._read_buffer) == 0:
            self._check_for_error()

        try:
            return self._read_buffer
        finally:
            self._read_buffer = bytearray()

    def _check_for_error(self):
        if self._error is None:
            return

        raise ConnectionClosedException(self._error)

    def unread(self, data):
        self._read_buffer = data + self._read_buffer

    def write(self, data, block_size=32, delay=0.01):
        raise NotImplementedError()

    def _log_data(self, data):
        print(
            data.decode("Latin-1")
            .replace("\r\n", "\n")
            .replace("\x01", "①")
            .replace("\x02", "②")
            .replace("\x03", "③")
            .replace("\x04", "④"),
            end="",
        )

    def incoming_is_empty(self):
        return self._read_queue.empty() and len(self._read_buffer) == 0

    def outgoing_is_empty(self):
        return True

    def buffers_are_empty(self):
        return self.incoming_is_empty() and self.outgoing_is_empty()

    def reset_input_buffer(self):
        return self.read_all()

    def reset_output_buffer(self):
        pass

    def close(self):
        raise NotImplementedError()


class ConnectionFailedException(Exception):
    pass


class ConnectionClosedException(Exception):
    pass
