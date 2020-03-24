import asyncio
import logging
from pyGizmoServer.utility import debug
from pyGizmoServer.controller import Controller


class MockUSB(Controller):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.callback = None
        self.msg = None
        self.ask = None
        self.logger = logging.getLogger('gizmoLogger')
        self.version = None
        self.floodrate = 0
        self.floodval = 0
        self.getversion = None

    def setup(self):
        debug("someone called me")
        if self.getversion is None:
            self.getversion = asyncio.Event()

    def setRelay(self, relay, state):
        debug("someone called me")

    def finished_processing_request(self):
        debug("someone called me")
        pass

    def sendrawusb(self, msg):
        print(msg)

    def setfloodrate(self, rate):
        self.floodrate = 1.0 / rate if rate else False

    async def getFirmwareVersion(self):
        self.ask = True
        self.getversion.clear()
        self.finished_processing_request()
        await self.getversion.wait()
        return self.version
        self.ask = None

    async def handler(self):
        self.running = True
        if self.floodrate:
            await asyncio.sleep(self.floodrate)
            self.floodval += 1
            self.floodval %= 10000
            self.send("/flood/monitor", self.floodval)
        if self.ask is not None:
            self.version = "6.6.6"
            self.getversion.set()
