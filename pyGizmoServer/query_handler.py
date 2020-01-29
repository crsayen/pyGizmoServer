import jsonpatch, json
import copy
from pubsub import pub
import io, copy, re, time
from pyGizmoServer.subscription_server import SubscriptionServer
from pyGizmoServer.utility import Utility

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
        pub.subscribe(self.handle_updates, 'received_update')
    
    def handle_get(self, path, address, response_handle=None):
        # ensure the path is valid, and formatted properly
        data = Utility.parse_path_against_schema_and_model(self.model, self.schema, path, read_write='r')
        if data["error"] is not None:
            response = data["error"]
            print(f"query_handler: {response}")
            pub.sendMessage(response_handle, response=response, fmt="HTML")
            return
        if data["routine"] is not None:
            data["model_data"] = getattr(self.controller, routine)(*data["args"])
            """TODO: update the model to reflect the data we get from the controller"""
        self.subscription_server.add(data["path_up_to_array_index"], address)
        if response_handle is not None:
            response = json.dumps({
                "path": data["path_string"],
                "data": data["model_data"]
            })
            pub.sendMessage(response_handle, response=response, fmt="HTML")
    
    def handle_updates(self, message):       
        self.subscription_server.parseupdate(message)