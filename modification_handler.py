import jsonpatch, patch_validation, json
from pubsub import pub 


class ModificationHandler:
    def __init__(endpoint, schema, default_model=None):
        self.endpoint = endpoint()
        self.schema = schema
        self.default_model = default_model
    
    def start(self):
        self.endpoint.start()
        pub.subscribe(self.handle_patch, 'modification_request_recieved')

    def handle_patch(self, requests):

