import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = ""
hostPort = 8069

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/JSON")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!


    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html(f"did get: {self.requestline}"))

    def do_PATCH(self):
        self._set_headers()
        self.wfile.write(self._html(f"did patch: {self.requestline}"))

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))