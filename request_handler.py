import socket, patch_validation, json, time, threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pubsub import pub


class PyGizmoRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _html(self, message):
        self._set_headers()
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8") 

    def _json(self, message):
        self._set_headers("application/JSON")
        content = f"{message}"
        return content.encode("utf8")


    def do_GET(self):
        self.wfile.write(self._html(f"did get: {self.requestline}"))
        
    def do_PATCH(self):
        self.response = None
        handle =  threading.currentThread().getName()
        pub.subscribe(self.post_response, handle)
        content = self.rfile.read(int(self.headers.get('Content-Length')))
        content = json.loads(content)
        requests = content if isinstance(content,list) else [content]
        for request in requests:
            try:
                    patch_validation.patch_validation_from_dict(request)
            except AssertionError:
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    f"invalid PATCH request format: {request}"
                )
        pub.sendMessage('modification_request_recieved', requests=requests, response_handle=handle)
        while self.response is None: pass
            
    def post_response(self, response):
        self.response = response
        self.wfile.write(self._json(f"{json.dumps(response)}"))

        
    