import asyncio
import json
import logging


class MockUSB:
    def __init__(self):
        self.callback = None
        self.msg = None
        self.ask = None
        self.logger = logging.getLogger('gizmoLogger')
        self.running = False
        self.version = None
        self.getversion = None
        self.onslaught = False
        self.relays = [False] * 6
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

    async def tend(self, func, args):
        if not self.running:
            await func(args, self.usbrxhandler())

    def setRelay(self, relay, state):
        self.relays[relay] = state
        self.msg = {
            "path": f"/relayController/relays",
            "data": self.relays,
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

    def flood(self, time):
        self.onslaught = time

    async def usbrxhandler(self):
        self.running = True
        if self.getversion is None:
            self.getversion = asyncio.Event()
        while 1:
            if self.onslaught:
                if self.msg is None:
                    self.msg = {
                        "path": f"/relayController/relays",
                        "data": [True] + ([False] * 5)
                    }
                old = self.msg['data']
                self.msg['data'] = old[1:] + old[:1]
                self.callback(self.msg)
                await asyncio.sleep(float(self.onslaught) / 1000)
            elif self.msg is not None:
                self.logger
                self.callback(self.msg)
                self.msg = None
            if self.ask is not None:
                self.version = "6.6.6"
                self.getversion.set()
            await asyncio.sleep(0)
