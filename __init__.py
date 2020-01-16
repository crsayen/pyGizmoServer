from http.server import HTTPServer
from socketserver import ThreadingMixIn
from request_handler import PyGizmoRequestHandler
from modification_handler import ModificationHandler
from endpoint import Endpoint
import time, json

mock_model = {
    "relayController": {
        "relays" : [
            { "enabled": False },
            { "enabled": False },
            { "enabled": False },
            { "enabled": False },
            { "enabled": False },
            { "enabled": False }
        ]
    }
}

hostName = ""
hostPort = 8020

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
    pass

with open('schemas/testcube_UI_schema.json') as f:
    hwschema = json.load(f)
modification_handler = ModificationHandler(Endpoint, hwschema, model=mock_model)
gizmoServer = ThreadedHTTPServer((hostName, hostPort), PyGizmoRequestHandler)
print(time.asctime(), "Server started - %s:%s" % (hostName, hostPort))

try:
    gizmoServer.serve_forever()
except KeyboardInterrupt:
    pass

gizmoServer.server_close()
print(time.asctime(), "Server Stopped - %s:%s" % (hostName, hostPort))