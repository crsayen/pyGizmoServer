import jsonpatch, json
import copy
from pubsub import pub
import asyncio
from pyGizmoServer.utility import *
from aiohttp import web

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
    """
    the handle_patch method is called when a 'modification_request_received'
    event is raised

    Parameters:
    requests (list): A list of modification requests 
    response_handle (string): A handle to a 'response' event subscriber
    """
    async def handle_patch_from_client(self, request):
        request = json.loads(await request.text())
        if not isinstance(request, list): request = [request]
        response = []
        for r in request:
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
        patch = jsonpatch.JsonPatch(request)
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        return web.json_response(response)
        

    """ this gets called by query_handler.py """
    def handle_patch_from_controller(self, updates=None, path=None, value=None):
        if updates is None:
            updates = [{"op": "replace", "path": path, "value": value}]
        patch = jsonpatch.JsonPatch(updates)
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        pub.sendMessage("applied_modification_from_controller", updates=updates)

    


    
