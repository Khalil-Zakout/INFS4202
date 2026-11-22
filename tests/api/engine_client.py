"""Zero-dependency JSON client for the UniPlace Engine (black-box).

Reads the base URL from the ENGINE_URL environment variable, defaulting to the
local Engine. No third-party packages are required: only the Python standard
library, so the suite runs on any machine with Python 3.8+.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("ENGINE_URL", "http://127.0.0.1:8081/api/v1")


class Response:
    def __init__(self, status: int, body: str, elapsed_ms: float):
        self.status = status
        self.text = body
        self.elapsed_ms = elapsed_ms
        try:
            self.json = json.loads(body) if body else None
        except json.JSONDecodeError:
            self.json = None

    def __repr__(self) -> str:
        return f"<{self.status} {self.text[:120]}>"


def call(path: str, body=None, method: str = "POST", raw: bytes | None = None,
         content_type: str = "application/json") -> Response:
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(BASE_URL + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", content_type)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status, text = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        status, text = err.code, err.read().decode("utf-8", "replace")
    return Response(status, text, (time.perf_counter() - start) * 1000)


def engine_available() -> bool:
    try:
        return call("/health", method="GET").status == 200
    except OSError:
        return False
