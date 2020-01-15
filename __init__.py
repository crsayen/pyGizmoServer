from http.server import HTTPServer
from socketserver import ThreadingMixIn
from request_handler import PyGizmoRequestHandler
from modification_handler import ModificationHandler
from endpoint import Endpoint
import time, json


hostName = ""
hostPort = 8020

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
    pass

with open('schemas/testcube_HW_schema.json') as f:
    hwschema = json.load(f)
modification_handler = ModificationHandler(Endpoint, hwschema)
gizmoServer = ThreadedHTTPServer((hostName, hostPort), PyGizmoRequestHandler)
print(time.asctime(), "Server started - %s:%s" % (hostName, hostPort))

try:
    gizmoServer.serve_forever()
except KeyboardInterrupt:
    pass

gizmoServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))