import asyncio
import logging
from pyGizmoServer.controller import Controller


class MockUSB(Controller):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.callback = None
        self.msg = None
        self.ask = None
        self.logger = logging.getLogger('gizmoLogger')
        self.version = None
        self.getversion = None
        self.onslaught = False
        self.relays = [False] * 6

    def setup(self):
        if self.getversion is None:
            self.getversion = asyncio.Event()

    def setRelay(self, relay, state):
        self.relays[relay] = state
        self.msg = {
            "path": f"/relayController/relays",
            "data": self.relays,
        }

    def finished_processing_request(self):
        pass

    def wsinvoke(self, msg):
        print(f"wsinvoke: {msg}")
        if self.msg is None:
            self.msg = {
                "path": "/wsinvoke",
                "data": "this message arrived via websocket",
            }

    async def getFirmwareVersion(self):
        print(id(asyncio.get_event_loop()))
        self.ask = True
        self.getversion.clear()
        self.finished_processing_request()
        await self.getversion.wait()
        return self.version

    async def handler(self):
        self.running = True
        if self.msg is not None:
            self.logger
            self.callback(self.msg)
            self.msg = None
        if self.ask is not None:
            self.version = "6.6.6"
            self.getversion.set()
