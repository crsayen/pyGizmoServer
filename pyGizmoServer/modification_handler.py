import json
import jsonpatch
import logging
from pyGizmoServer.utility import Utility, debug
from aiohttp import web
from aiojobs.aiohttp import spawn


class ModificationHandler:
    def __init__(self, controller, model=None):
        self.controller = controller
        self.schema = controller.schema
        self.logger = logging.getLogger("gizmoLogger")
        debug("init")
        self.model = model

    async def handle_patch_from_client(self, request):
        if not self.controller.running:
            await spawn(request, self.controller.usbrxhandler())
        request = json.loads(await request.text())
        debug(f"{request}")
        if not isinstance(request, list):
            request = [request]
        response = []
        for r in request:
            path = r.get("path")
            if path is None:
                raise ValueError(f"no path provided in request: {r}")
            data = Utility.parse_path_against_schema_and_model(
                self.model, self.schema, path, read_write="w"
            )
            if data["error"] is not None:
                self.logger.error(f"{data['error']}")
                return web.json_response([{"error": data["error"]}])
            value = r.get("value")
            if value is not None:
                data["args"].append(value)
            # call the specified function with the associated parameters
            try:
                getattr(self.controller, data["routine"])(*data["args"])
            except Exception as e:
                debug(f"{e}")
                data["error"] = f"bad request: {r}\n{e}"
                return web.json_response([{"error": data["error"]}])
            r["path"] = data["path_string"]
            response.append({"path": data["path_string"], "data": value})
        self.controller.finished()
        """
        create and apply the requested PATCH to the model
        """
        patch = jsonpatch.JsonPatch(request)
        jsonpatch.apply_patch(self.model, patch, in_place=True)
        return web.json_response(response)
