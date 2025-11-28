from __future__ import annotations

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PaymentEventLogger:
    """Best-effort emitter for payment events (e.g., to context-graph)."""

    def __init__(self, client=None):
        self.client = client

    def log_event(
        self,
        *,
        event_type: str,
        subject_id: str,
        person_id: str,
        provider: str | None,
        status: str,
        amount: float | None = None,
        currency: str | None = None,
        counterparty: str | None = None,
        surface: str | None = None,
        instrument_kind: str | None = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "event_type": event_type,
            "subject_id": subject_id,
            "person_id": person_id,
            "provider": provider,
            "status": status,
            "amount": amount,
            "currency": currency,
            "counterparty": counterparty,
            "surface": surface,
            "instrument_kind": instrument_kind,
        }
        if not self.client:
            logger.debug("payment event (local): %s", payload)
            return
        try:
            ok, status_code, _ = self.client.post("/payments/events", payload)
            if not ok or status_code >= 300:
                logger.debug("payment event emit failed: status=%s ok=%s payload=%s", status_code, ok, payload)
        except Exception as exc:
            logger.debug("payment event emit exception: %s", exc)
