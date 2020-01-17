import jsonpatch, json
import copy
from pubsub import pub
import io, copy, re
from pyGizmoServer.subscription_server import SubscriptionServer

class QueryHandler:
    """
    This class handles client queries. It looks at the device model and update
    messages from the device to generate query responses, and publish update
    streams via a Websocket server

    Attributes:
    controller (controller): A controller for some pice of hardware
    schema (dict): A description of the hardware that controller is based on
    default_model (dict): An in-memory model of the hardware
    """
    def __init__(self, address, controller, schema, model=None):
        self.controller = controller
        self.schema = schema
        self.model = model
        self.err = None
        self.address = address
        self.subscritpion_server = SubscriptionServer(self.address)
        self.subscribers = {}
        pub.subscribe(self.handle_get, 'query_request_recieved')
        pub.subscribe(self.handle_updates, 'received_update')
    
    def handle_get(self, path, address, response_handle=None):
        # ensure the path is valid, and formatted properly
        result = self.parse_and_validate_path(path)
        if not result:
            response = f"Invalid path: {path}"
            pub.sendMessage(response_handle, response=response, fmt="HTML")
            return
        self.subscritpion_server.add(result["subscribable_path"], address)
        if response_handle is not None:
            response = json.dumps({
                "path": result["query_path"],
                "data": result["query_data"]
            })
            pub.sendMessage(response_handle, response=response, fmt="HTML")

    def parse_and_validate_path(self, path):
        # remove formatting characters, and split on path delimeters
        paths = re.split('. |/', path.strip('\n\r\t'))
        paths.remove('')
        # ensure each destination on the path is a valid destination on the model
        location = copy.deepcopy(self.model)
        n_valid_destinations = 0
        for i, p in enumerate(paths):
            if p == '': break
            try:
                if p.isnumeric():
                    n_valid_destinations = i
                    p = int(p)
                location = location[p]
            except Exception as e:
                if self.err is None: self.err = ''
                self.err+= f"Path error: {p}\nException: {e}\n"
        if self.err is not None:
            print(self.err)
            return False
        return {
            "subscribable_path": '/'.join(paths[:n_valid_destinations]),
            "query_path": '/'.join(paths),
            "query_data": location            
        }

    def handle_updates(self, message):
        print(f"message:\n{message}\n\n")
        self.subscritpion_server.publish(message)