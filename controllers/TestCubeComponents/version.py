class VersionMessage:
    def __init__(self):
        self.ask = None
        pass

    def getFirmwareVersion(self):
        self.ask = True

    def get_version_messages(self):
        if self.ask == None:
            return []
        return [f"{0x40:08x}"]
