from http.server import HTTPServer
from socketserver import ThreadingMixIn
from pyGizmoServer.request_handler import PyGizmoRequestHandler
from pyGizmoServer.modification_handler import ModificationHandler
from pyGizmoServer.query_handler import QueryHandler
from controllers.testcube_usb_controller import TestCubeUSB
from controllers.mock_controller import MockUSB
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
    },
    "adcController": {
        "adcs" : [
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 },
            { "measuredCurrent": 0 }
        ]
    }
}
address = ('', 8020)

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
    pass

with open('schemas/testcube_HW.json') as f:
    hwschema = json.load(f)
#controller = TestCubeUSB()
controller = MockUSB()
controller.start()
modification_handler = ModificationHandler(controller, hwschema, model=mock_model)
query_handler = QueryHandler(address, controller, hwschema, model=mock_model)
gizmoServer = ThreadedHTTPServer(address, PyGizmoRequestHandler)
print(time.asctime(), f"Server started - {address}")

try:
    gizmoServer.serve_forever()
except KeyboardInterrupt:
    pass

gizmoServer.server_close()
print(time.asctime(), f"Server started - {address}")