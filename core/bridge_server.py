import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt6.QtCore import QObject, pyqtSignal

DEFAULT_BRIDGE_PORT = 48911

class BridgeRequestHandler(BaseHTTPRequestHandler):
    bridge_instance = None

    def log_message(self, format, *args):
        pass  # Quiet logging

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = json.dumps({"status": "running", "app": "OmniDL Pro", "port": DEFAULT_BRIDGE_PORT}).encode("utf-8")
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

    def do_POST(self):
        if self.path == "/download" or self.path == "/capture":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode("utf-8"))

                if BridgeRequestHandler.bridge_instance:
                    BridgeRequestHandler.bridge_instance.stream_captured.emit(payload)

                self.send_response(200)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Stream sent to OmniDL"}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

class BridgeServer(QObject):
    """Local loopback bridge server allowing browser extension to send captured streams."""
    stream_captured = pyqtSignal(dict)  # emits {url, pageUrl, title, headers}

    def __init__(self, port=DEFAULT_BRIDGE_PORT, parent=None):
        super().__init__(parent)
        self.port = port
        self.httpd = None
        self.server_thread = None
        BridgeRequestHandler.bridge_instance = self

    def start(self):
        try:
            self.httpd = ReusableHTTPServer(("127.0.0.1", self.port), BridgeRequestHandler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
        except Exception as e:
            pass

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
