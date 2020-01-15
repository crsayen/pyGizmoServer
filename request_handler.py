import socket, jsonpatch, patch_validation, json, time
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
        s = time.time()
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
        patch = jsonpatch.JsonPatch(requests)
        result = jsonpatch.apply_patch(mock_model, patch)
        pub.sendMessage('modification_request_recieved', requests=requests)
        self.wfile.write(self._json(json.dumps(result)))
        
    