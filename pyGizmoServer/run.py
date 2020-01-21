from http.server import HTTPServer
from socketserver import ThreadingMixIn
from pyGizmoServer.request_handler import PyGizmoRequestHandler
from pyGizmoServer.modification_handler import ModificationHandler
from pyGizmoServer.query_handler import QueryHandler
from controllers.testcube_usb_controller import TestCubeUSB
from controllers.mock_controller import MockUSB
import sys
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
    "pwmController": {
        "bankA": {
            "frequency": 0,
        },
        "bankB": {
            "frequency": 0,
        },
        "pwms" : [
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False },
            { "dutyCycle": 0,
            "enabled": False }
        ]
    }
}
address = ('', 36364)

def main():
    class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
        pass

    with open('schemas/testcube_HW.json') as f:
        hwschema = json.load(f)
    if len(sys.argv) > 1 and sys.argv[1] in ["--test", "-t"]:
        controller = MockUSB()
    else:
        controller = TestCubeUSB()

    controller.start()
    modification_handler = ModificationHandler(controller, hwschema, model=mock_model)
    query_handler = QueryHandler(address, controller, hwschema, model=mock_model)
    modification_handler.start()
    query_handler.start()
    gizmoServer = ThreadedHTTPServer(address, PyGizmoRequestHandler)
    print(time.asctime(), f"Server started - {address}")

    try:
        gizmoServer.serve_forever()
    except KeyboardInterrupt:
        pass

    gizmoServer.server_close()
    print(time.asctime(), f"Server started - {address}")

if __name__ == "__main__":
    main()