import websockets
import json
import asyncio
import logging


class SubscriptionServer:
    def __init__(self, ws_ip, ws_port):
        self.logger = logging.getLogger("gizmoLogger")
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{ws_ip},{ws_port}")
        self.connected = set()
        self.subscribers = {}
        self.server = websockets.serve(self.connection_handler, ws_ip, ws_port)
        asyncio.get_event_loop().run_until_complete(self.server)

    async def publish(self, updates):
        for update in updates:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"{updates}")
            path = update.get("path")
            if path is None:
                raise ValueError(f"unable to publish update, bad format: {updates}")
            try:
                for connection in self.connected:
                    if connection[1] in path:
                        if self.logger.isEnabledFor(logging.DEBUG):
                            self.logger.debug(f"sending ws: {update}")
                        await connection[0].send(json.dumps(update))
            except Exception as e:
                self.logger.error(f"{e}")

    async def connection_handler(self, websocket, path):
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{path}")
        connection = (websocket, path)
        self.connected.add(connection)
        await connection[0].send(f"SUCCESS: you are subscribed to {path}")
        await websocket.wait_closed()
        self.connected.remove(connection)
