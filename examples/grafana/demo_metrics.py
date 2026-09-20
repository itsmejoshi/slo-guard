"""Tiny dependency-free metrics source for the Grafana integration demo.

Endpoints:
  /metrics   Prometheus text exposition
  /burn      simulate a high error rate
  /recover   return to the healthy error rate
  /healthz   basic health check
"""
from __future__ import annotations

import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 8000

_lock = threading.Lock()
_last_update = time.monotonic()
_success_total = 10_000.0
_error_total = 1.0
_mode = "normal"

SUCCESS_RATE_PER_SECOND = 50.0
NORMAL_ERROR_RATE_PER_SECOND = 0.01
BURN_ERROR_RATE_PER_SECOND = 2.0


def _advance() -> None:
    global _last_update, _success_total, _error_total
    now = time.monotonic()
    elapsed = max(0.0, now - _last_update)
    _success_total += SUCCESS_RATE_PER_SECOND * elapsed
    error_rate = (
        BURN_ERROR_RATE_PER_SECOND if _mode == "burn" else NORMAL_ERROR_RATE_PER_SECOND
    )
    _error_total += error_rate * elapsed
    _last_update = now


class Handler(BaseHTTPRequestHandler):
    def _write(self, status: int, body: str, content_type: str = "text/plain; charset=utf-8") -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        global _mode
        if self.path == "/healthz":
            self._write(200, "ok\n")
            return

        if self.path in {"/burn", "/recover"}:
            with _lock:
                _advance()
                _mode = "burn" if self.path == "/burn" else "normal"
            self._write(200, f"mode={_mode}\n")
            return

        if self.path == "/metrics":
            with _lock:
                _advance()
                success = _success_total
                errors = _error_total
                mode = _mode

            metrics = (
                "# HELP http_requests_total Simulated HTTP requests for the slo-guard demo.\n"
                "# TYPE http_requests_total counter\n"
                f'http_requests_total{{code="200"}} {success:.6f}\n'
                f'http_requests_total{{code="500"}} {errors:.6f}\n'
                "# HELP slo_guard_demo_mode Demo mode: 1 for the active mode.\n"
                "# TYPE slo_guard_demo_mode gauge\n"
                f'slo_guard_demo_mode{{mode="{mode}"}} 1\n'
            )
            self._write(200, metrics, "text/plain; version=0.0.4; charset=utf-8")
            return

        self._write(404, "not found\n")

    def log_message(self, fmt: str, *args: object) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving demo metrics on http://{HOST}:{PORT}/metrics", flush=True)
    server.serve_forever()
