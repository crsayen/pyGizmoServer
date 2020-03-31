import asyncio
import logging
from pyGizmoServer.utility import debug
from TestCubeUSB.getter import get


class VersionMessage():
    def __init__(self):
        self.getVersionEvent = None
        self.ask = None
        pass

    async def getFirmwareVersion(self, retry=0):
        self.ask = True
        if await get(self.finished_processing_request,self.getVersionEvent):
            return self.version
        print("version ded")

    def get_version_messages(self):
        if self.ask is None:
            return []
        return [f"{0x50:08x}"]

    def rec_usb_51_version(self, payload):
        debug(f"{payload}")
        if len(payload) < 12:
            self.version = "0.0.0"
        else:
            hi, lo, patch = (
                int(payload[:4], 16),
                int(payload[4:8], 16),
                int(payload[8:12], 16),
            )
            self.version = f"{hi}.{lo}.{patch}"
        if self.getVersionEvent is None:
            self.getVersionEvent = asyncio.Event()
        if not self.getVersionEvent.is_set():
            self.getVersionEvent.set()
        return [{"path": "/version", "data": self.version}]
