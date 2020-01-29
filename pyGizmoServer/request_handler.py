import socket, json, time, threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pyGizmoServer import patch_validation
from pubsub import pub


class PyGizmoRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def send(self, message, fmt):
        if fmt.upper() == "HTML":
            self._set_headers()
            content = f"<html><body><p>{message}</p></body></html>"
            return content.encode("utf8") 
        if fmt.upper() == "JSON":
            self._set_headers("application/JSON")
            content = f"{message}"
            return content.encode("utf8")  

    def do_GET(self):
        print(f"received a GET request: {self.path}")
        handle = self.generate_response_handler()
        pub.sendMessage('query_request_recieved', path=self.path, address=self.client_address, response_handle=handle)
        
    def do_PATCH(self):
        self.response = None
        handle = self.generate_response_handler()
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
        pub.sendMessage('modification_request_recieved_from_client', requests=requests, response_handle=handle)
        while self.response is None: pass

    def generate_response_handler(self):
        handle =  threading.currentThread().getName()
        pub.subscribe(self.post_response, handle)
        return handle
            
    def post_response(self, response, fmt):
        self.response = response
        self.wfile.write(self.send(f"{json.dumps(response)}", fmt))

        
    