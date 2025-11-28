import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Allow running tests from workspace with sibling unison-common present.
ROOT = Path(__file__).resolve().parents[2]
COMMON_SRC = ROOT / "unison-common" / "src"
if COMMON_SRC.exists():
    sys.path.insert(0, str(COMMON_SRC))

from payments.server import app


def test_auth_can_be_disabled_for_tests(monkeypatch):
    monkeypatch.setenv("DISABLE_AUTH_FOR_TESTS", "true")
    client = TestClient(app)
    payload = {
        "person_id": "p1",
        "provider": "mock",
        "kind": "card",
        "last4": "4242",
        "token": "tok_123",
    }
    resp = client.post("/payments/instruments", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["ok"] is True
    assert body["instrument"]["person_id"] == "p1"
