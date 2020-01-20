import jsonpatch, json
import copy
from pubsub import pub
import asyncio
from pyGizmoServer.utility import *

class ModificationHandler:
    """
    This class takes requests and calls hardware related functions on
    an 'controller' object written for specific hardware

    Attributes:
    controller (controller): A controller for some pice of hardware
    schema (dict): A description of the hardware that controller is based on
    default_model (dict): An in-memory model of the hardware
    """
    def __init__(self, controller, schema, model=None):
        self.controller = controller
        self.schema = schema
        self.model = model

    def start():
        pub.subscribe(self.handle_patch, 'modification_request_recieved')
    
    """
    the handle_patch method is called when a 'modification_request_received'
    event is raised

    Parameters:
    requests (list): A list of modification requests 
    response_handle (string): A handle to a 'response' event subscriber
    """
    def handle_patch(self, requests, response_handle=None):
        for r in requests:
            response = []
            data = Utility.parse_path_against_schema_and_model(self.model, self.schema, path, read_write='w')
            if data["error"] is not None:
                print(f"modification handler: {data["error"]}")
                continue
            value = r.get("value")
            if value is not None: data["args"].append(value)
            # call the specified function with the associated parameters
            getattr(self.controller, routine)(*data["args"])
            """
            rebuild the path. This corrects any index-notation issues 
            that the original path may have had
            """
            r["path"] = data["path_string"]
            response.append({"path": data["path_string"], "data": value})
        self.controller.finished()
        """
        create and apply the requested PATCH to the model
        """
        patch = jsonpatch.JsonPatch(requests)
        result = jsonpatch.apply_patch(self.model, patch)
        """
        if someone is subscribed to response events, raise an event
        """
        if response_handle is not None:
            pub.sendMessage(response_handle, response=response, fmt="JSON")

    


    
