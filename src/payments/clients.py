from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import httpx

JsonDict = Dict[str, Any]
HttpResult = Tuple[bool, int, Optional[JsonDict]]


def _merge_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    return dict(headers or {})


@dataclass
class ServiceHttpClient:
    host: str
    port: str

    def get(self, path: str, *, headers: Optional[Dict[str, str]] = None) -> HttpResult:
        merged_headers = _merge_headers(headers)
        try:
            resp = httpx.get(f"http://{self.host}:{self.port}{path}", headers=merged_headers or None, timeout=2.0)
            ok = resp.status_code < 300
            body = resp.json() if resp.content else None
            return ok, resp.status_code, body
        except Exception:
            return False, 500, None

    def post(self, path: str, payload: JsonDict, *, headers: Optional[Dict[str, str]] = None) -> HttpResult:
        merged_headers = _merge_headers(headers)
        try:
            resp = httpx.post(
                f"http://{self.host}:{self.port}{path}",
                headers=merged_headers or None,
                json=payload,
                timeout=2.0,
            )
            ok = resp.status_code < 300
            body = resp.json() if resp.content else None
            return ok, resp.status_code, body
        except Exception:
            return False, 500, None
