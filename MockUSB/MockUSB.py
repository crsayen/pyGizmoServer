import asyncio
import json
import logging
from pyGizmoServer.utility import debug


class MockUSB:
    def __init__(self):
        self.callback = None
        self.msg = None
        self.ask = None
        self.logger = logging.getLogger('gizmoLogger')
        self.running = False
        self.version = None
        self.getversion = None
        with open("MockUSB/schema.json") as f:
            self.schema = json.load(f)

    def setcallback(self, callback):
        if not callable(callback):
            raise ValueError("callback must be a function")
        self.callback = callback

    def start(self):
        if self.callback is None:
            raise RuntimeError("controller callback not set")
        pass

    def setRelay(self, relay, state):
        debug(f"{relay=}{state=}")
        self.msg = {
            "path": f"/relayController/relays/{relay}",
            "data": state,
        }

    def finished(self):
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
        self.finished()
        await self.getversion.wait()
        return [{"path": "/version", "data": self.version}]

    async def usbrxhandler(self):
        self.running = True
        if self.getversion is None:
            self.getversion = asyncio.Event()
        while 1:
            if self.msg is not None:
                self.logger
                self.callback(self.msg)
                self.msg = None
            if self.ask is not None:
                self.version = "6.6.6"
                self.getversion.set()
            await asyncio.sleep(0.001)
