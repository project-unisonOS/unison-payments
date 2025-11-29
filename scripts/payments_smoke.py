"""In-process smoke test for unison-payments.

Runs the FastAPI app in-process (no network) with auth disabled and asserts that
basic instrument/transaction flows succeed.
"""
import os
from fastapi.testclient import TestClient

os.environ.setdefault("DISABLE_AUTH_FOR_TESTS", "true")

from payments.server import app  # noqa: E402


def run_smoke():
    client = TestClient(app)
    inst_payload = {
        "person_id": "smoke-person",
        "provider": "mock",
        "kind": "card",
        "last4": "4242",
        "token": "tok_smoke",
    }
    resp = client.post("/payments/instruments", json=inst_payload)
    assert resp.status_code == 200, resp.text
    instrument = resp.json()["instrument"]

    txn_payload = {
        "person_id": instrument["person_id"],
        "instrument_id": instrument["instrument_id"],
        "amount": 1.23,
        "currency": "USD",
        "authorization_context": {"approved": True},
    }
    resp = client.post("/payments/transactions", json=txn_payload)
    assert resp.status_code == 200, resp.text
    txn = resp.json()["transaction"]

    resp = client.get(f"/payments/transactions/{txn['txn_id']}")
    assert resp.status_code == 200, resp.text
    print("Payments smoke passed", {"instrument": instrument["instrument_id"], "txn": txn["txn_id"]})


if __name__ == "__main__":
    run_smoke()
