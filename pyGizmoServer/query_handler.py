import jsonpatch, json, itertools
from itertools import zip_longest
import copy
from pubsub import pub
import dpath.util
import io, copy, re, time
from pyGizmoServer.subscription_server import SubscriptionServer
from pyGizmoServer.utility import Utility
from aiohttp import web

def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        d = dict(a)
        d.update({k: merge(a.get(k, None), b[k]) for k in b})
        return d

    if isinstance(a, list) and isinstance(b, list):
        return [merge(x, y) for x, y in itertools.zip_longest(a, b)]

    return a if b is None else b

class QueryHandler:
    """
    This class handles client queries. It looks at the device model and update
    messages from the device to generate query responses, and publish update
    streams via a Websocket server

    Attributes:
    controller (controller): A controller for some piece of hardware
    schema (dict): A description of the hardware that controller is based on
    default_model (dict): An in-memory model of the hardware
    """
    def __init__(self, address, schema, model=None):
        self.schema = schema
        self.model = model
        self.err = None
        self.address = address
        self.subscription_server = SubscriptionServer(address)
        self.subscribers = {}

    def add_controller(self, controller):
        self.controller = controller
    
    def handle_get(self, request):
        path = request.path
        print(f"query_handler: handle_get: {path}")
        data = Utility.parse_path_against_schema_and_model(self.model, self.schema, path, read_write='r')
        if data["error"] is not None:
            response = data["error"]
            print(f"ERROR: query_handler: {response}")
            return
        if data.get("routine") is not None:
            data["model_data"] = getattr(self.controller, data["routine"])(*data["args"])
        return web.json_response(data)

    async def handle_updates(self, updates): 
        print(f"query_handler: handle_updates: update received: {updates}")
        outgoing = []
        if not isinstance(updates, list):
            updates = [updates]
        for update in updates:
            if isinstance(update, str) or (data := update.get("data")) is None or (path := update.get("path")) is None: 
                print("handle_updates: ERROR path or data key not found")
                continue
            location = dpath.util.get(self.model, path)
            result = merge(location, data)
            outgoing.append({"path": path, "value": data})
        print(f"outgoing updates: {outgoing}")
        await self.subscription_server.publish(outgoing)