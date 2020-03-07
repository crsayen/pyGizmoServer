import json
import asyncio


class Controller():
    def __init__(self):
        self.running = False
        self.callback = None
        with open(f"{self.__class__.__name__}/schema.json") as f:
            self.schema = json.load(f)

    async def handlerloop(self):
        while 1:
            await self.handler()
            await asyncio.sleep(0)

    def start(self):
        if self.callback is None:
            raise RuntimeError("controller callback not set")
        if hasattr(self, 'setup'):
            self.setup()

    async def tend(self, func, args):
        if not self.running:
            await func(args, self.handlerloop())
        self.running = True

    def setcallback(self, callback):
        if not callable(callback):
            raise ValueError("callback must be a function")
        self.callback = callback

    async def handler(self):
        raise NotImplementedError

    def finished_processing_request(self):
        raise NotImplementedError

    def send(self, path, data):
        self.callback({
            "path": path,
            "data": data
        })
