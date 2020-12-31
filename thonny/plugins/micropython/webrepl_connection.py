import sys
import threading
import time
from queue import Queue

from thonny.common import ConnectionFailedException
from thonny.plugins.micropython.connection import MicroPythonConnection

DEBUG = False


class WebReplConnection(MicroPythonConnection):
    """
    Problem with block size:
    https://github.com/micropython/micropython/issues/2497
    Start with conservative delay.
    Client may later reduce it for better efficiency
    """

    def __init__(self, url, password):

        self.num_bytes_received = 0
        super().__init__()

        try:
            import websockets  # @UnusedImport
        except:
            print(
                "Can't import `websockets`. You can install it via 'Tools => Manage plug-ins'.",
                file=sys.stderr,
            )
            sys.exit(-1)
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

    def _wrap_ws_main(self):
        import asyncio

        loop = asyncio.new_event_loop()
        loop.set_debug(DEBUG)
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
        import websockets

        try:
            try:
                self._ws = await websockets.connect(self._url, ping_interval=None)
            except websockets.exceptions.InvalidMessage:
                # try once more
                self._ws = await websockets.connect(self._url, ping_interval=None)
        except OSError as e:
            # print("\nCould not connect:", e, file=sys.stderr)
            raise ConnectionFailedException(str(e))
        debug("GOT WS", self._ws)

        # read password prompt and send password
        read_chars = ""
        while read_chars != "Password: ":
            debug("prelude", read_chars)
            ch = await self._ws.recv()
            debug("GOT", ch)
            read_chars += ch

        debug("sending password")
        await self._ws.send(self._password + "\n")
        debug("sent password")

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
                if isinstance(data, WebreplBinaryMsg):
                    payload = data.data
                else:
                    payload = data.decode("UTF-8")
                await self._ws.send(payload)
                debug("Wrote bytes", len(data))
                self._write_responses.put(len(data))

            # Allow reading loop to progress
            await asyncio.sleep(0.01)

    def write(self, data):
        self._write_queue.put_nowait(data)
        return self._write_responses.get()

    async def _async_close(self):
        await self._ws.close()

    def close_and_return_new_connection(self):
        self.close()
        return WebReplConnection(self._url, self._password)

    def close(self):
        """
        # TODO:
        import asyncio
        asyncio.get_event_loop().run_until_complete(self.async_close())
        """


class WebreplBinaryMsg:
    """This wrapper helps distinguishing between bytes which should
    be decoded and sent as text frame and bytes sent as binary frame"""

    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)


def debug(*args):
    if DEBUG:
        print(*args, file=sys.stderr)
