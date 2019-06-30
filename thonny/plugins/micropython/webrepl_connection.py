from thonny.plugins.micropython.connection import MicroPythonConnection
from queue import Queue
import threading


class WebReplConnection(MicroPythonConnection):
    def __init__(self, url, password):
        super().__init__()
        self._url = url
        self._password = password

        # Some tricks are needed to use async library in sync program
        # use thread-safe queues to communicate with async world in another thread
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
        import asyncio
        import websockets

        self._ws = await asyncio.wait_for(websockets.connect(self._url, ping_interval=None), 3)
        print("GOT WS", self._ws)

        # read password prompt and send password
        read_chars = ""
        while read_chars != "Password: ":
            print("prelude", read_chars)
            ch = await self._ws.recv()
            print("GOT", ch)
            read_chars += ch

        print("sending password")
        await self._ws.send(self._password + "\n")
        print("sent password")

    async def _ws_keep_reading(self):
        while True:
            data = (await self._ws.recv()).encode("UTF-8")
            if len(data) == 0:
                self._error = "EOF"
                break

            self.num_bytes_received += len(data)
            self._read_queue.put(data, block=False)

    async def _ws_keep_writing(self):
        import asyncio

        while True:
            while not self._write_queue.empty():
                data = self._write_queue.get(block=False).decode("UTF-8")
                print("Wrote:", repr(data))
                await self._ws.send(data)
            # Allow reading loop to progress
            await asyncio.sleep(0.01)

    def write(self, data, block_size=32, delay=0.01):
        self._write_queue.put_nowait(data)

    async def _async_close(self):
        await self._ws.close()

    def close(self):
        """
        import asyncio
        asyncio.get_event_loop().run_until_complete(self.async_close())
        """
