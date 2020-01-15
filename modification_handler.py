import jsonpatch, patch_validation, json
from pubsub import pub 

mock_model = {
    "relays" : [
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 0 } },
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 1 } },
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 2 } },
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 3 } },
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 4 } },
        { "enabled": { "r": "getRelay", "w": "setRelay", "args": 5 } }
    ]
}

def setRelay(r, s):
    print(f"set relay {r}: {s}")

class ModificationHandler:
    def __init__(self, endpoint, schema, default_model=None):
        self.endpoint = endpoint()
        self.schema = schema
        self.default_model = default_model
        self.endpoint.start()
        pub.subscribe(self.handle_patch, 'modification_request_recieved')
    
    def handle_patch(self, requests, response_handle = None):
        
        for r in requests:
            data = self.schema
            paths = r["path"].replace('/', '.').split('.')
            print(paths)
            for i, path in enumerate(paths):
                if path == '': continue
                print(f"{data}\n\n")
                print(f"{path}\n")
                if path[-1] == ']':
                    path, istr = path.replace(']', '').split("[")
                    data = data[path][int(istr)]
                    paths[i] = f"{path}/{istr}"
                    continue
                data = data[path]
            r["path"] = "/".join(paths)
            print(data)
        patch = jsonpatch.JsonPatch(requests)
        result = jsonpatch.apply_patch(mock_model, patch)
        if response_handle is not None:
            pub.sendMessage(response_handle, response=result)
