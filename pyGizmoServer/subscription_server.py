import websockets
import json
import asyncio
import logging
import threading
import dpath
from pyGizmoServer.utility import debug


class SubscriptionServer:
    def __init__(self, ws_ip, ws_port):
        self.logger = logging.getLogger("gizmoLogger")
        if self.logger.isEnabledFor(logging.DEBUG):
            debug(f"{ws_ip},{ws_port}")
        self.connected = set()
        self.subscribers = {}
        self.ip = ws_ip
        self.port = ws_port
        threading.Thread(target=self.run_server(), args=()).start()

    def run_server(self):
        self.subloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.subloop)
        self.server = websockets.serve(
            self.connection_handler,
            self.ip, self.port,
            loop=self.subloop,
            max_size=1024
        )
        self.subloop.run_until_complete(self.server)

    def publish(self, update):
        debug(f"{update['path']}")
        path = update.get("path")
        for con, sub in [
            connection for connection in self.connected
            if path in connection[1] or path == connection[1]
        ]:
            debug(path)
            data = {
                "path": sub,
                "value": dpath.util.get(
                    update["value"],
                    sub[len(path):]
                )
            } if path != sub else update
            debug(f"sending ws on: {data}")
            asyncio.run_coroutine_threadsafe(
                con.send(json.dumps(data)), self.subloop
            )

    async def connection_handler(self, websocket, path):
        debug(f"NEW CONNECTION: {path}")
        connection = (websocket, path)
        self.connected.add(connection)
        await websocket.wait_closed()
        debug(f"DISCONNECTED: {path}")
        self.connected.remove(connection)
