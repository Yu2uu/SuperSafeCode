"""Local-only HTTP fixture missing nosniff, used to validate ZAP's blocking rule."""

from http.server import BaseHTTPRequestHandler, HTTPServer


class MissingHeaderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<!doctype html><title>ZAP negative control</title><p>Fixture only</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8001), MissingHeaderHandler).serve_forever()
