import queue
import re
import time
from logging import getLogger
from queue import Queue
from typing import Optional, Union

logger = getLogger(__name__)


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
        self.text_mode = True
        self._error = None
        self._reader_stopped = False

    def soft_read(self, size: int, timeout: float = 1) -> bytes:
        return self.read(size, timeout, True)

    def read(self, size: int, timeout: float = 10, timeout_is_soft: bool = False) -> bytes:
        if timeout == 0:
            if timeout_is_soft:
                return b""
            else:
                raise ReadingTimeoutError(read_bytes=b"")

        timer = TimeHelper(timeout)

        while len(self._read_buffer) < size:
            self.check_for_error()

            try:
                self._read_buffer.extend(self._read_queue.get(True, timer.time_left))
            except queue.Empty:
                if timeout_is_soft:
                    return b""
                else:
                    logger.error(
                        "Could not read expected %s bytes in %s seconds. Bytes read: %r",
                        size,
                        timeout,
                        self._read_buffer,
                    )
                    raise ReadingTimeoutError(read_bytes=self._read_buffer)

        try:
            data = self._read_buffer[:size]
            return data
        finally:
            del self._read_buffer[:size]

    def soft_read_until(self, terminator, timeout: float = 1000000) -> bytes:
        return self.read_until(terminator, timeout, timeout_is_soft=True)

    def read_until(
        self,
        terminator: Union[bytes, re.Pattern],
        timeout: float = 1000000,
        timeout_is_soft: bool = False,
    ) -> bytes:
        timer = TimeHelper(timeout)

        if isinstance(terminator, bytes):
            terminator = re.compile(re.escape(terminator))

        assert isinstance(terminator, re.Pattern)

        while True:
            self.check_for_error()

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
                    raise ReadingTimeoutError(read_bytes=self._read_buffer)

        if match:
            size = match.end()
        else:
            assert timeout_is_soft
            size = len(self._read_buffer)

        data = self._read_buffer[:size]
        del self._read_buffer[:size]
        return data

    def _fetch_to_buffer(self) -> None:
        while not self._read_queue.empty():
            self._read_buffer.extend(self._read_queue.get(True))

    def read_all(self, check_error: bool = True) -> bytes:
        self._fetch_to_buffer()

        if len(self._read_buffer) == 0 and check_error:
            self.check_for_error()

        try:
            return self._read_buffer
        finally:
            self._read_buffer = bytearray()

    def read_all_expected(self, expected: bytes, timeout: float = None) -> bytes:
        actual = self.read(len(expected), timeout=timeout)
        actual += self.read_all()
        assert expected == actual, "Expected %r, got %r" % (expected, actual)
        return actual

    def check_for_error(self) -> None:
        if self._error is None:
            return
        logger.info("Detected connection error")
        raise ConnectionError(self._error)

    def unread(self, data: bytes) -> None:
        if not data:
            return

        if isinstance(data, str):
            data = data.encode(self.encoding)
        elif isinstance(data, bytes):
            data = bytearray(data)

        self._read_buffer = data + self._read_buffer

    def write(self, data: bytes) -> int:
        """Writing"""
        raise NotImplementedError()

    def _log_data(self, data: bytes) -> None:
        print(
            data.decode(self.encoding, errors="replace")
            .replace("\r\n", "\n")
            .replace("\x01", "①")
            .replace("\x02", "②")
            .replace("\x03", "③")
            .replace("\x04", "④"),
            end="",
        )

    def _make_output_available(self, data: bytes, block: bool = True) -> None:
        # self._log_data(data)
        if data:
            self._read_queue.put(data, block=block)
            self.num_bytes_received += len(data)

    def incoming_is_empty(self) -> bool:
        return self._read_queue.empty() and len(self._read_buffer) == 0

    def outgoing_is_empty(self) -> bool:
        return True

    def buffers_are_empty(self) -> bool:
        return self.incoming_is_empty() and self.outgoing_is_empty()

    def set_text_mode(self, value: bool) -> None:
        self.text_mode = value

    def stop_reader(self) -> None:
        self._reader_stopped = True
        self._read_queue = Queue()
        self._read_buffer = bytearray()

    def close(self) -> None:
        raise NotImplementedError()


class ReadingTimeoutError(TimeoutError):
    def __init__(self, read_bytes: bytes):
        super().__init__(f"Read bytes: {read_bytes}")
        self.read_bytes = read_bytes


class TimeHelper:
    def __init__(self, time_allowed):
        self.start_time = time.time()
        self.time_allowed = time_allowed

    @property
    def time_spent(self):
        return time.time() - self.start_time

    @property
    def time_left(self):
        return max(self.time_allowed - self.time_spent, 0)
