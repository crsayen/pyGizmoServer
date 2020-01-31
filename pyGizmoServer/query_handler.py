import jsonpatch, json, itertools
from itertools import zip_longest
import copy
from pubsub import pub
import dpath.util
import io, copy, re, time
from pyGizmoServer.subscription_server import SubscriptionServer
from pyGizmoServer.utility import Utility

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
    def __init__(self, address, controller, schema, model=None):
        self.controller = controller
        self.schema = schema
        self.model = model
        self.err = None
        self.address = address
        self.subscribers = {}

    def start(self):
        self.subscription_server = SubscriptionServer(self.address)
        pub.subscribe(self.handle_get, 'query_request_recieved')
        pub.subscribe(self.handle_updates, 'update_received')
    
    def handle_get(self, path, address, response_handle=None):
        # ensure the path is valid, and formatted properly
        print(f"query_handler: handle_get: {path}")
        data = Utility.parse_path_against_schema_and_model(self.model, self.schema, path, read_write='r')
        if data["error"] is not None:
            response = data["error"]
            print(f"query_handler: {response}")
            pub.sendMessage(response_handle, response=response, fmt="HTML")
            return
        if data.get("routine") is not None:
            data["model_data"] = getattr(self.controller, data["routine"])(*data["args"])
            """TODO: update the model to reflect the data we get from the controller"""
        if response_handle is not None:
            response = json.dumps({
                "path": data["path_string"],
                "data": data["model_data"]
            })
            pub.sendMessage(response_handle, response=json.dumps(response,indent=2), fmt="HTML")

    def handle_updates(self, message): 
        print(f"query_handler: handle_updates: update received: {message}")
        outgoing = []
        for update in message:
            path = update["path"]
            data = update["data"]
            location = dpath.util.get(self.model, path)
            result = merge(location, data)
            outgoing.append({"path": path, "value": data})
        self.subscription_server.publish(outgoing)