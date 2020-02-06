import asyncio, json


class MockUSB:
    def __init__(self, callback):
        self.callback = callback
        self.msg = None

    def start(self):
        pass

    def setRelay(self, relay, state):
        pass

    def finished(self):
        pass

    def wsinvoke(self, msg):
        print(f"wsinvoke: {msg}")
        if self.msg is None:
            self.msg = msg

    async def usbrxhandler(self):
        while 1:
            if self.msg is not None:
                print(f"handler: {self.msg}")
                await self.callback(self.msg)
                self.msg = None
            await asyncio.sleep(0.001)
