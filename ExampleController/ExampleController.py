import asyncio
from pyGizmoServer.utility import log
from pyGizmoServer.controller import Controller


class ExampleController(Controller):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.counter = 0
        self.strings = ["a", "b", "c"]
        self.concat = ''.join(self.strings)
        self.stridx = 0

    """
    Setup gets called once at startup.
    Use this to do any initialization your controller requires
    """
    def setup(self):
        log("someone called me")

    def setString(self, index, value):
        self.strings[index] = value

    async def getString(self, index):
        return self.strings[index]

    """
    This gets called after the server processes a request.
    """
    def finished_processing_request(self):
        log("someone called me")

    """
    The handler gets called repeatedly.
    Use this to send real time updates to the client
    """
    async def handler(self):
        await asyncio.sleep(0.2)
        self.concat = self.strings[self.stridx]
        self.stridx += 1
        self.stridx %= 3
        self.counter += 1
        self.counter %= 100
        self.send("/watch_me_concatenate", self.concat)
        self.send("/watch_me_count", self.counter)
