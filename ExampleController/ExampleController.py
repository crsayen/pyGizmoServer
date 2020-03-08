import asyncio
import random
from pyGizmoServer.utility import log
from pyGizmoServer.controller import Controller


class ExampleController(Controller):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.counter = 0
        self.strings = ["a", "b", "c"]
        self.read_idx = 0

    """
    This gets called after the server processes a request.
    """
    def finished_processing_request(self):
        log("someone called me")

    """
    Setup gets called once at startup.
    Use this to do any initialization your controller requires
    """
    def setup(self):
        log("someone called me")

    def setString(self, index, value):
        self.strings[index] = value

    async def getnumber(self):
        return random.randint(0, 100)

    """
    The handler gets called repeatedly.
    Use this to send real time updates to the client
    """
    async def handler(self):
        await asyncio.sleep(0.2)
        self.read_idx += 1
        self.read_idx %= 3
        self.send("/watch_me_read", self.strings[self.read_idx])
