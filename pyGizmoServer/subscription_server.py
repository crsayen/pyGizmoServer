import websockets, json, threading, asyncio, copy
from queue import Queue
import logging

class SubscriptionServer:
    def __init__(self,ws_ip, ws_port):
        self.logger = logging.getLogger('gizmoLogger')
        self.logger.debug(f'SubscriptionServer({ws_ip=},{ws_port=})')
        self.connected = set()
        self.subscribers = {}
        self.server = websockets.serve(self.connection_handler, ws_ip, ws_port)
        asyncio.get_event_loop().run_until_complete(self.server)

    async def publish(self, updates):
        for update in updates:
            self.logger.debug(f"SubscriptionServer.publish: {updates}")
            if (path := update.get("path")) is None:
                raise ValueError(f"unable to publish update, bad format: {updates}")
            for connection in self.connected:
                if connection[1] in path:
                    try:
                        result = await connection[0].send(json.dumps(update))
                    except Exception as e:
                        self.logger.error(f'{e}')
  
    async def connection_handler(self, websocket, path):
        self.logger.debug(f"SubscriptionServer.connection_handler: {websocket}")
        connection = (websocket, path)
        self.connected.add(connection)
        result = await connection[0].send(f'SUCCESS: you are subscribed to {path}')
        await websocket.wait_closed()
        self.connected.remove(connection)



