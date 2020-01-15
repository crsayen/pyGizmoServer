import jsonpatch, patch_validation, json
from pubsub import pub 

mock_model = {"state": "michigan"}

class ModificationHandler:
    def __init__(self, endpoint, schema, default_model=None):
        self.endpoint = endpoint()
        self.schema = schema
        self.default_model = default_model
        self.endpoint.start()
        pub.subscribe(self.handle_patch, 'modification_request_recieved')
    
    def handle_patch(self, requests, response_handle = None):
        patch = jsonpatch.JsonPatch(requests)
        result = jsonpatch.apply_patch(mock_model, patch)
        if response_handle is not None:
            pub.sendMessage(response_handle, response=result)
