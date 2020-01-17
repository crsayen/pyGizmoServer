import websockets, json, threading, asyncio

class SubscriptionServer:
    def __init__(self,address):
        self.address = ('127.0.0.1', 8021)
        self.connected = set()
        self.subscribers = {}
        self.server = None
        self.thread_run = threading.Thread(target=self.run_async,args=([]))
        self.thread_run.start()

    def add(self, path, address):
        if address[0] not in self.subscribers:
            self.subscribers[address[0]] = {path}
        else: self.subscribers[address[0]].add(path)

    def remove(self, address):
        try:
            del self.subscribers[address[0]]
        except Exception as e:
            pass
            #print(f"failed to remove {address}:\n{e}")

    def publish(self, message):
        if not isinstance(message, dict) or (path := message.get("path")) is None:
            #print(f"subscription_server.publish: invalid message: {message}")
            return
        for subscriber, subscriptions in self.subscribers.items():
            for subscription in subscriptions:
                if subscription in path:
                    message = json.dumps(message)
                    self.send_message(message)

    async def send_message(self, message):
        await asyncio.wait(websocket.send(f"{{\n\t'path':{path},\n\t'value':{value}}}"))

    async def handler(websocket, path):
        # register the client
        connected.add(websocket)
        try:
            await asyncio.sleep(10)
        finally:
            # unregister the client
            connected.remove(websocket)
            self.remove(websocket)

    def run_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.server = websockets.serve(self.handler, *self.address)
        loop.run_until_complete(self.server)
        loop.run_forever()


