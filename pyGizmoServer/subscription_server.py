import websockets, json, threading, asyncio, copy
from pubsub import pub

class SubscriptionServer:
    def __init__(self,address):
        self.address = ('127.0.0.1', 8021)
        self.connected = set()
        self.subscribers = {}
        self.server = None
        self.thread_run = threading.Thread(target=self.run_async,args=([]))
        self.thread_run.start()
        pub.subscribe(self.publish, 'applied_modification_from_controller')

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

    def parsedict(self, path, d):
        for k,v in d.items():
            if isinstance(v, list): 
                self.parselist(path + f"/{k}")
            elif isinstance(v, dict):
                self.parsedict(path + f"/{k}")
            else:
                self.applyupdate(path + f"/{k}", v)

    def parselist(self, path, l):
        for i, item in enumerate(l):
            if isinstance(item, list): 
                self.parselist(path + f"/{i}")
            elif isinstance(item, dict):
                self.parsedict(path + f"/{i}")
            else:
                self.applyupdate(path + f"/{i}", item)

    def parseupdate(self, update):
        if isinstance(update, dict): self.parsedict('', update)
        elif isinstance(update, list): 
            for item in update:
                if not isinstance(item, dict):
                    raise ValueError(f"incorrect update format: {update}")
                self.parsedict('',update)

    def applyupdate(self, path, value):
        pub.sendMessage('modification_request_recieved_from_controller', path=path, value=value)

    def publish(self, message):
        for update in message:
            if (path := message.get("path")) is None:
                raise ValueError(f"unable to publish update, bad format: {message}")
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


