import jsonpatch, json
import copy
from pubsub import pub
import asyncio
from pyGizmoServer.utility import *
from aiohttp import web

class ModificationHandler:
    def __init__(self, controller, schema, model=None):
        self.controller = controller
        self.schema = schema
        self.model = model

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
            
            r["path"] = data["path_string"]
            response.append({"path": data["path_string"], "data": value})
        self.controller.finished()
        """
        create and apply the requested PATCH to the model
        """
        patch = jsonpatch.JsonPatch(request)
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        return web.json_response(response)
        
    def handle_patch_from_controller(self, updates=None, path=None, value=None):
        if updates is None:
            updates = [{"op": "replace", "path": path, "value": value}]
        patch = jsonpatch.JsonPatch(updates)
        jsonpatch.apply_patch(self.model, patch,in_place=True)
        pub.sendMessage("applied_modification_from_controller", updates=updates)

    


    
