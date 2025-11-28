from __future__ import annotations

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import register_payment_routes
from .clients import ServiceHttpClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unison Payments", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


def _build_client_from_env(prefix: str) -> ServiceHttpClient | None:
    host = os.getenv(f"{prefix}_HOST")
    port = os.getenv(f"{prefix}_PORT")
    if not host or not port:
        return None
    return ServiceHttpClient(host, port)


context_client = _build_client_from_env("UNISON_CONTEXT")
storage_client = _build_client_from_env("UNISON_STORAGE")

register_payment_routes(app, context_client=context_client, storage_client=storage_client)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("payments.server:app", host="0.0.0.0", port=8089, reload=True)
