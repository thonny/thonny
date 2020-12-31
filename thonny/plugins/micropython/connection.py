import queue
import re
import time
from queue import Queue

from thonny.common import ConnectionClosedException
from thonny.misc_utils import TimeHelper


class MicroPythonConnection:
    """Utility class for using Serial or WebSocket connection

    Uses background thread to read from the source as soon as possible
    to avoid loss of data (because buffer overflow or the device discarding
    unread data).

    Allows unreading data.
    """

    def __init__(self):
        self.encoding = "utf-8"
        self._read_queue = Queue()  # populated by reader thread
        self._read_buffer = bytearray()  # used for unreading and postponing bytes
        self.num_bytes_received = 0
        self.startup_time = time.time()
        self.unicode_guard = True
        self._error = None
        self._reader_stopped = False

    def soft_read(self, size, timeout=1):
        return self.read(size, timeout, True)

    def read(self, size, timeout=10, timeout_is_soft=False):
        if timeout == 0:
            if timeout_is_soft:
                return b""
            else:
                raise TimeoutError()

        timer = TimeHelper(timeout)

        while len(self._read_buffer) < size:
            self._check_for_error()

            try:
                self._read_buffer.extend(self._read_queue.get(True, timer.time_left))
            except queue.Empty:
                if timeout_is_soft:
                    return b""
                else:
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

    def read_all(self, check_error=True):
        self._fetch_to_buffer()

        if len(self._read_buffer) == 0 and check_error:
            self._check_for_error()

        try:
            return self._read_buffer
        finally:
            self._read_buffer = bytearray()

    def read_all_expected(self, expected, timeout=None):
        actual = self.read(len(expected), timeout=timeout)
        actual += self.read_all()
        assert expected == actual, "Expected %r, got %r" % (expected, actual)

    def _check_for_error(self):
        if self._error is None:
            return

        raise ConnectionClosedException(self._error)

    def unread(self, data):
        if not data:
            return

        if isinstance(data, str):
            data = data.encode(self.encoding)
        elif isinstance(data, bytes):
            data = bytearray(data)

        self._read_buffer = data + self._read_buffer

    def write(self, data):
        raise NotImplementedError()

    def _log_data(self, data):
        print(
            data.decode(self.encoding, errors="replace")
            .replace("\r\n", "\n")
            .replace("\x01", "①")
            .replace("\x02", "②")
            .replace("\x03", "③")
            .replace("\x04", "④"),
            end="",
        )

    def _make_output_available(self, data, block=True):
        # self._log_data(data)
        if data:
            self._read_queue.put(data, block=block)
            self.num_bytes_received += len(data)

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

    def set_unicode_guard(self, value):
        self.unicode_guard = value

    def stop_reader(self):
        self._reader_stopped = True
        self._read_queue = Queue()
        self._read_buffer = bytearray()

    def close(self):
        raise NotImplementedError()
