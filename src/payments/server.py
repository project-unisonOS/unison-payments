from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import register_payment_routes

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


# In a full deployment, wire context/storage clients with auth here.
register_payment_routes(app)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("payments.server:app", host="0.0.0.0", port=8089, reload=True)
