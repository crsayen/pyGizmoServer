import websockets
import json
import asyncio
import threading
from typing import Dict, List, Any, Set
from dpath.util import get
from pyGizmoServer.utility import debug


class SubscriptionServer:
    """Maintains and services websocket connections.

        Keeps track of connected peers, and the paths
        they are connected to, sending updates as they
        arrive. Clients can 'subscribe' to the controller
        by connecting to it's paths as websocket URLs.

        Attributes:
            connected: Set -- (websocket: websocket, path: str)
            ip: str -- The IP address we serve on.
            port: int -- The port we serve on.
            subloop: asyncio.Loop -- An event loop that runs in
                a parallel thread, servicing connections.
    """

    def __init__(self, ws_ip, ws_port):
        debug(f"{ws_ip},{ws_port}")
        self.connected: Set = set()
        self.ip: str = ws_ip
        self.port: int = ws_port
        threading.Thread(self.run_server()).start()

    def run_server(self) -> None:
        """Starts the server running.

            sets up subloop, and runs the server in it.
        """
        self.subloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.subloop)
        self.server = websockets.serve(
            self.connection_handler,
            self.ip,
            self.port,
            loop=self.subloop,
            max_size=1024,
        )
        try:
            self.subloop.run_until_complete(self.server)
        except:
            print("\n\nRUN_SERVER\n\nCAUGHT EXCEPTION\n\n")

    def publish(self, update: Dict[str, Any]) -> None:
        """Sends updates to any connected 'subscribers'

            Looks through self.connected for any subscribers
            whose subscription scope covers any updated data,
            and sends that data to them.

        Arguments:
            update {Dict} -- path/data update from the controller
        """
        debug(f"{update}")
        path = update.get("path")
        for con, sub in [
            connection
            for connection in self.connected
            if path in connection[1] or path == connection[1]
        ]:
            if path != sub:
                # checks if we are looking up array index - breaks dpath.util.get
                if sub[len(path) :][1].isnumeric():
                    data = {
                        "path": sub,
                        "value": get(update["value"], sub[len(path) :]),
                    }
                else:
                    data = {
                        "path": sub,
                        "value": get(update["value"], sub[len(path) :]),
                    }
            else:
                data = update
            debug(f"sending ws on: {data}")
            asyncio.run_coroutine_threadsafe(con.send(json.dumps(data)), self.subloop)

    async def connection_handler(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ) -> None:
        """Connects to, adds, and awaits connected peers.

            Adds the connectors (websocket, path) to self.connected
            and awaits the closing of the connection.
        """
        debug(f"NEW CONNECTION: {path}")
        connection = (websocket, path)
        self.connected.add(connection)
        await websocket.wait_closed()
        debug(f"DISCONNECTED: {path}")
        self.connected.remove(connection)
