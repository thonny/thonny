import queue
from thonny.misc_utils import TimeHelper
from queue import Queue
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

    def read_until(self, terminator, timeout=1000000, timeout_is_soft=False):
        timer = TimeHelper(timeout)
        if isinstance(terminator, (set, list, tuple)):
            terminators = terminator
        else:
            terminators = [terminator]

        terminator = None
        while True:
            self._check_for_error()

            found = False
            for terminator in terminators:
                if terminator in self._read_buffer:
                    found = True
                    break
            if found:
                break

            try:
                data = self._read_queue.get(True, timer.time_left)
                assert len(data) > 0
                self._read_buffer.extend(data)
            except queue.Empty:
                if timeout_is_soft:
                    break
                else:
                    raise TimeoutError("Reaction timeout. Bytes read: %s" % self._read_buffer)

        assert terminator is not None
        size = self._read_buffer.index(terminator) + len(terminator)

        try:
            data = self._read_buffer[:size]
            return data
        finally:
            del self._read_buffer[:size]

    def read_all(self):
        while not self._read_queue.empty():
            self._read_buffer.extend(self._read_queue.get(True))

        if len(self._read_buffer) == 0:
            self._check_for_error()

        try:
            return self._read_buffer
        finally:
            self._read_buffer = bytearray()

    def _check_for_error(self):
        if self._error:
            # TODO:
            raise EOFError("EOF")

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

class ConnectionClosedException(Exception):
    pass

