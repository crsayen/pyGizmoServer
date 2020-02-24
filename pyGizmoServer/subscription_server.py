import websockets
import json
import asyncio
import logging
import threading


class SubscriptionServer:
    def __init__(self, ws_ip, ws_port):
        self.logger = logging.getLogger("gizmoLogger")
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{ws_ip},{ws_port}")
        self.connected = set()
        self.subscribers = {}
        self.ip = ws_ip
        self.port = ws_port
        threading.Thread(target=self.run_server(), args=()).start()

    def run_server(self):
        self.subloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.subloop)
        self.server = websockets.serve(
            self.connection_handler, self.ip, self.port, loop=self.subloop, max_size=1024
        )
        self.subloop.run_until_complete(self.server)
        

    def publish(self, update):
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{update['path']}")
        path = update.get("path")
        if path is None:
            raise ValueError(f"unable to publish update, bad format: {update}")
        #try:
        for connection in self.connected:
            if path == connection[1]:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"sending ws on: {update}")
                asyncio.run_coroutine_threadsafe(
                    connection[0].send(json.dumps(update)), self.subloop
                )
            elif path in connection[1]:
                locupdate = update["value"].copy()
                locpath = connection[1][len(path):]
                for p in locpath.split('/'):
                    if p == '': 
                        continue
                    if p.isnumeric():
                        p = int(p)
                    locupdate = locupdate[p]
                newupdate = {"path": connection[1], "value": locupdate}
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"sending ws on: {newupdate}")
                asyncio.run_coroutine_threadsafe(
                    connection[0].send(json.dumps(newupdate)), self.subloop
                    )
        #except Exception as e:
            #self.logger.error(f"{e}")

    async def connection_handler(self, websocket, path):
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{path}")
        connection = (websocket, path)
        self.connected.add(connection)
        await websocket.wait_closed()
        self.connected.remove(connection)
