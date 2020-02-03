import websockets, json, threading, asyncio, copy
from queue import Queue
from pubsub import pub
import logging

class SubscriptionServer:
    def __init__(self,address):
        self.address = ('0.0.0.0', 36364)
        self.logger = logging.getLogger('websockets')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.connected = set()
        self.subscribers = {}
        self.server = websockets.serve(self.handler, "0.0.0.0", 11111)
        asyncio.get_event_loop().run_until_complete(self.server)

    async def publish(self, updates):
        for update in updates:
            print(f"\nsubscription_server: publish: {updates=}")
            if (path := update.get("path")) is None:
                raise ValueError(f"unable to publish update, bad format: {updates}")
            for connection in self.connected:
                if connection[1] in path:
                    result = await connection[0].send(json.dumps(update))
  
    async def handler(self, websocket, path):
        connection = (websocket, path)
        self.connected.add(connection)
        print(f"\nsubscription_server: handler: new subscription: {self.connected=}")
        #await websocket.wait_closed()




