import jsonpatch, json
import copy
from pubsub import pub
import asyncio

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
            """
            navigate the schema following the request's path. The destination
            should be the name of a function and associated parameters that this 
            method will call
            """
            index = None
            data = copy.deepcopy(self.schema)
            paths = r["path"].replace('/', '.').split('.')
            for i, path in enumerate(paths):
                if path == '': continue

                """ 
                check if the request utilizes array indexing 
                and if so, store the index to pass to the controller
                """
                if path[-1] == ']':
                    path, istr = path.replace(']', '').split("[")
                    data = data[path]
                    paths[i] = f"{path}/{istr}"
                    index = int(istr)
                    continue
                """ 
                check if the path is an array index and if so, 
                store the index to pass to the controller
                """
                if path.isnumeric():
                    index = int(path)
                    continue
                data = data[path]
            routine = data['w']
            args = data.get('args')
            if index is not None: args.append(index)
            value = r.get("value")
            if value is not None: args.append(value)
            # call the specified function with the associated parameters
            getattr(self.controller, routine)(*args)
            """
            rebuild the path. This corrects any index-notation issues 
            that the original path may have had
            """
            r["path"] = "/".join(paths)
        self.controller.xmit()
        """
        create and apply the requested PATCH to the model
        """
        patch = jsonpatch.JsonPatch(requests)
        result = jsonpatch.apply_patch(self.model, patch)
        """
        if someone is subscribed to response events, raise an event
        """
        if response_handle is not None:
            pub.sendMessage(response_handle, response=result)

    


    
