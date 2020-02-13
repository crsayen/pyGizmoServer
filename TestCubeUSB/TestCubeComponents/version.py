import asyncio


class VersionMessage:
    def __init__(self):
        self.ask = None
        pass

    async def getFirmwareVersion(self):
        self.ask = True
        if self.getVersionEvent is None:
            self.getVersionEvent = asyncio.Event()
        else:
            self.getVersionEvent.clear()
        self.finished()
        await self.getVersionEvent.wait()
        return [{"path": "/version", "data": self.version}]

    def get_version_messages(self):
        if self.ask is None:
            return []
        return [f"{0x50:08x}"]

    def recusb_41_version(self, payload):
        if len(payload) < 12:
            self.version = "0.0.0"
        else:
            hi, lo, patch = (
                int(payload[:4], 16),
                int(payload[4:8], 16),
                int(payload[8:12], 16),
            )
            self.version = f"{hi}.{lo}.{patch}"
        if not self.getVersionEvent.is_set():
            self.getVersionEvent.set()
        return [{"path": "/version", "data": self.version}]
