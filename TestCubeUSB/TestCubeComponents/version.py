class VersionMessage:
    def __init__(self):
        self.ask = None
        pass

    async def getFirmwareVersion(self):
        self.ask = True
        self.getversion.clear()
        self.finished()
        await self.getversion.wait()
        return [{"path": "/version", "data": self.version}]

    def get_version_messages(self):
        if self.ask is None:
            return []
        return [f"{0x40:08x}"]
