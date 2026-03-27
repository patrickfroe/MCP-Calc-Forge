from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.mcp.discovery import build_discovery_payload


class DiscoveryRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/discovery":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))
            return

        payload = build_discovery_payload()
        response_bytes = json.dumps(payload).encode("utf-8")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def run_discovery_http_server(host: str = "127.0.0.1", port: int = 8090) -> None:
    with ThreadingHTTPServer((host, port), DiscoveryRequestHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    run_discovery_http_server()
