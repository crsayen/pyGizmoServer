import websockets, json, threading, asyncio, copy
from queue import Queue
from pubsub import pub

class SubscriptionServer:
    def __init__(self,address):
        self.address = ('0.0.0.0', 36364)
        self.connected = set()
        self.subscribers = {}
        self.server = None
        self.thread_run = threading.Thread(target=self.run_async,args=([]))
        self.thread_run.start()

    def publish(self, updates):
        for update in updates:
            print(f"\nsubscription_server: publish: {updates=}")
            if (path := update.get("path")) is None:
                raise ValueError(f"unable to publish update, bad format: {updates}")
            for connection in self.connected:
                if connection[0] in path:
                    print(f"\nfound subscriber")
                    connection[1].put(item=update)
  
    async def handler(self, websocket, path):
        # register the client
        outbox = Queue()
        async def send_message(message):
            print(f"\nsubscription_server: send_message: {message}")
            await websocket.send(json.dumps(message))
        connection = (path, outbox)
        self.connected.add(connection)
        print(f"\nsubscription_server: handler: new subscription: {self.connected=}")
        while True:
            if outbox.empty(): continue
            message = outbox.get()
            print(f"{message=}")
            result = await websocket.send("hello")
            print(f"we got here {result}")

    def run_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.server = websockets.serve(self.handler, "0.0.0.0", 11111)
        loop.run_until_complete(self.server)
        loop.run_forever()


