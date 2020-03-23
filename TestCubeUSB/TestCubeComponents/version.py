import asyncio
import logging
from pyGizmoServer.utility import debug


class VersionMessage():
    def __init__(self):
        self.ask = None
        pass

    async def getFirmwareVersion(self, retry=0):
        self.ask = True
        self.finished_processing_request()
        if self.getVersionEvent is None:
            self.getVersionEvent = asyncio.Event()
        else:
            self.getVersionEvent.clear()
        try:
            await asyncio.wait_for(self.getVersionEvent.wait(), timeout=0.1)
        except:
            if retry < 5:
                return await self.getFirmwareVersion(retry = retry + 1)
            raise RuntimeError("getFirmwareVersion not responding")
        return self.version

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
        if self.getVersionEvent is not None and not self.getVersionEvent.is_set():
            self.getVersionEvent.set()
        return [{"path": "/version", "data": self.version}]
