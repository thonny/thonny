import sys
import threading
from logging import DEBUG, getLogger
from queue import Queue

from ...common import execute_with_frontend_sys_path
from .connection import MicroPythonConnection

logger = getLogger(__name__)


class WebReplConnection(MicroPythonConnection):
    """
    Problem with block size:
    https://github.com/micropython/micropython/issues/2497
    Start with conservative delay.
    Client may later reduce it for better efficiency
    """

    def __init__(self, url, password, num_bytes_received=0):
        self.num_bytes_received = num_bytes_received
        super().__init__()

        execute_with_frontend_sys_path(self._try_load_websockets)
        self._url = url
        self._password = password
        self._write_responses = Queue()

        # Some tricks are needed to use async library in a sync program.
        # Using thread-safe queues to communicate with async world in another thread
        self._write_queue = Queue()
        self._connection_result = Queue()
        self._ws_thread = threading.Thread(target=self._wrap_ws_main, daemon=True)
        self._ws_thread.start()

        # Wait until connection was made
        res = self._connection_result.get()
        if res != "OK":
            raise res

    def _try_load_websockets(self):
        try:
            import websockets
        except ImportError:
            logger.error("Could not import websockets")
            print(
                "Can't import `websockets`. You can install it via 'Tools => Manage plug-ins'.",
                file=sys.stderr,
            )
            sys.exit(1)

    def _wrap_ws_main(self):
        import asyncio

        loop = asyncio.new_event_loop()
        if logger.isEnabledFor(DEBUG):
            loop.set_debug(True)
        loop.run_until_complete(self._ws_main())

    async def _ws_main(self):
        import asyncio

        try:
            await self._ws_connect()
        except Exception as e:
            self._connection_result.put_nowait(e)
            return

        self._connection_result.put_nowait("OK")
        await asyncio.gather(self._ws_keep_reading(), self._ws_keep_writing())

    async def _ws_connect(self):
        import websockets.exceptions

        try:
            try:
                self._ws = await websockets.connect(self._url, ping_interval=None)
            except websockets.exceptions.InvalidMessage:
                # try once more
                self._ws = await websockets.connect(self._url, ping_interval=None)
        except OSError as e:
            # print("\nCould not connect:", e, file=sys.stderr)
            raise ConnectionRefusedError(str(e))
        logger.debug("GOT WS: %r", self._ws)

        # read password prompt and send password
        read_chars = ""
        logger.debug("Looking for password prompt")
        while read_chars != "Password: ":
            ch = await self._ws.recv()
            read_chars += ch

        logger.debug("Submitting password")
        await self._ws.send(self._password + "\n")

    async def _ws_keep_reading(self):
        import websockets.exceptions

        while not self._reader_stopped:
            try:
                data = await self._ws.recv()
                if isinstance(data, str):
                    data = data.encode("UTF-8")
                if len(data) == 0:
                    self._error = "EOF"
                    break
            except websockets.exceptions.ConnectionClosedError:
                # TODO: try to reconnect in case of Ctrl+D
                self._error = "EOF"
                break

            self.num_bytes_received += len(data)
            self._make_output_available(data, block=False)

    async def _ws_keep_writing(self):
        import asyncio

        while True:
            while not self._write_queue.empty():
                data = self._write_queue.get(block=False)
                if self.text_mode:
                    payload = data.decode("UTF-8")
                else:
                    payload = data
                await self._ws.send(payload)
                # logger.debug("Wrote %r bytes", len(data))
                self._write_responses.put(len(data))

            # Allow reading loop to progress
            await asyncio.sleep(0.01)

    def write(self, data: bytes) -> int:
        self._write_queue.put_nowait(data)
        return self._write_responses.get()

    async def _async_close(self):
        await self._ws.close()

    def close_and_return_new_connection(self):
        self.close()
        return WebReplConnection(self._url, self._password, self.num_bytes_received)

    def close(self):
        """
        # TODO:
        import asyncio
        asyncio.get_event_loop().run_until_complete(self.async_close())
        """
