from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from unison_common.http_client import http_get_json_with_retry, http_post_json_with_retry
from unison_common.baton import get_current_baton

JsonDict = Dict[str, Any]
HttpResult = Tuple[bool, int, Optional[JsonDict]]

_CALL_DEFAULTS = dict(max_retries=3, base_delay=0.1, max_delay=2.0, timeout=2.0)


def _merge_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    merged = dict(headers or {})
    baton = get_current_baton()
    if baton:
        merged.setdefault("X-Context-Baton", baton)
    return merged


@dataclass
class ServiceHttpClient:
    host: str
    port: str

    def get(self, path: str, *, headers: Optional[Dict[str, str]] = None) -> HttpResult:
        merged_headers = _merge_headers(headers)
        return http_get_json_with_retry(self.host, self.port, path, headers=merged_headers or None, **_CALL_DEFAULTS)

    def post(self, path: str, payload: JsonDict, *, headers: Optional[Dict[str, str]] = None) -> HttpResult:
        merged_headers = _merge_headers(headers)
        return http_post_json_with_retry(
            self.host,
            self.port,
            path,
            payload,
            headers=merged_headers or None,
            **_CALL_DEFAULTS,
        )
