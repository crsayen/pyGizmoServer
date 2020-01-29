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

    def start(self):
        pub.subscribe(self.handle_patch_from_client, 'modification_request_recieved_from_client')
        pub.subscribe(self.handle_patch_from_controller, 'modification_request_recieved_from_controller')
    
    """
    the handle_patch method is called when a 'modification_request_received'
    event is raised

    Parameters:
    requests (list): A list of modification requests 
    response_handle (string): A handle to a 'response' event subscriber
    """
    def handle_patch_from_client(self, requests, response_handle=None):
        print(f"modification_handler: handle_path_from_client")
        response = []
        for r in requests:
            if (path := r.get("path")) is None:
                raise ValueError(f"no path provided in request: {r}")
            data = Utility.parse_path_against_schema_and_model(self.model, self.schema, path, read_write='w')
            if data["error"] is not None:
                print(f"modification handler: {data['error']}")
                continue
            value = r.get("value")
            if value is not None: data["args"].append(value)
            # call the specified function with the associated parameters
            print(f"modification_handler: handle patch: {data['routine']=}")
            getattr(self.controller, data["routine"])(*data["args"])
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
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        """
        if someone is subscribed to response events, raise an event
        """
        if response_handle is not None:
            pub.sendMessage(response_handle, response=response, fmt="JSON")

    def handle_patch_from_controller(self, requests=None, path=None, value=None):
        if requests is None:
            requests = [{"op": "replace", "path": path, "value": value}]
        patch = jsonpatch.JsonPatch(requests)
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        pub.sendMessage("applied_modification_from_controller", requests=requests)

    


    
