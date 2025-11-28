from __future__ import annotations

import os
import uuid
import logging
from typing import Dict, Any

from fastapi import APIRouter, Body, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from .models import PaymentInstrument, PaymentTransactionRequest
from .providers import MockPaymentProvider, PaymentProvider
from .service import PaymentService
from .logging import PaymentEventLogger
from .auth import auth_dependency

_logger = logging.getLogger(__name__)

_require_payment_approval = os.getenv("UNISON_REQUIRE_PAYMENT_APPROVAL", "true").lower() in {"1", "true", "yes", "on"}


class PaymentInstrumentPayload(BaseModel):
    person_id: str = Field(..., description="Owner of the instrument")
    provider: str = Field(default="mock", description="Payment provider ID")
    kind: str = Field(default="mock", description="Instrument kind (card, bank, paypal, etc.)")
    display_name: str | None = None
    brand: str | None = None
    last4: str | None = None
    expiry: str | None = None
    handle: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    token: str | None = Field(default=None, description="Tokenized provider reference (no PAN/ACH)")


class PaymentTransactionPayload(BaseModel):
    person_id: str
    instrument_id: str
    amount: float
    currency: str = "USD"
    description: str | None = None
    counterparty: str | None = None
    authorization_context: Dict[str, Any] = Field(default_factory=dict)
    surface: str | None = Field(default=None, description="Requesting surface (voice, text, app)")


def register_payment_routes(app, *, context_client=None, storage_client=None) -> PaymentService:
    api = APIRouter()
    provider_name = os.getenv("UNISON_PAYMENTS_PROVIDER", "mock")
    provider: PaymentProvider
    if provider_name == "mock":
        provider = MockPaymentProvider()
    else:
        _logger.warning("Unsupported provider '%s'; defaulting to mock. Extend providers to add real PSPs.", provider_name)
        provider = MockPaymentProvider()

    service = PaymentService(
        provider,
        PaymentEventLogger(),
        context_client=context_client,
        storage_client=storage_client,
    )

    @api.post("/payments/instruments")
    def register_instrument(
        payload: PaymentInstrumentPayload = Body(...),
        current_user: Dict[str, Any] = Depends(auth_dependency),
    ):
        instrument = PaymentInstrument(
            instrument_id=str(uuid.uuid4()),
            person_id=payload.person_id,
            provider=payload.provider,
            kind=payload.kind,
            display_name=payload.display_name,
            brand=payload.brand,
            last4=payload.last4,
            expiry=payload.expiry,
            handle=payload.handle,
            metadata=payload.metadata,
        )
        registered = service.register_instrument(instrument, token=payload.token)
        return {"ok": True, "instrument": registered.__dict__}

    @api.post("/payments/transactions")
    def create_transaction(
        payload: PaymentTransactionPayload = Body(...),
        current_user: Dict[str, Any] = Depends(auth_dependency),
    ):
        if _require_payment_approval and not payload.authorization_context.get("approved"):
            raise HTTPException(status_code=403, detail="payment requires explicit approval")
        request = PaymentTransactionRequest(
            person_id=payload.person_id,
            instrument_id=payload.instrument_id,
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            counterparty=payload.counterparty,
            authorization_context=payload.authorization_context,
            surface=payload.surface,
        )
        txn = service.create_transaction(request)
        return {"ok": True, "transaction": txn.__dict__}

    @api.get("/payments/transactions/{txn_id}")
    def get_transaction_status(txn_id: str, current_user: Dict[str, Any] = Depends(auth_dependency)):
        try:
            txn = service.get_transaction_status(txn_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="transaction not found")
        return {"ok": True, "transaction": txn.__dict__}

    @api.post("/payments/webhooks/{provider}")
    async def provider_webhook(provider: str, request: Request):
        raw_body = await request.body()
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        if isinstance(payload, dict):
            payload["_raw_body"] = raw_body.decode("utf-8")
        try:
            txn = service.process_webhook(provider, payload)
        except ValueError:
            raise HTTPException(status_code=404, detail="unknown provider")
        except KeyError:
            raise HTTPException(status_code=404, detail="transaction not found")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"webhook processing failed: {exc}")
        return {"ok": True, "transaction": txn.__dict__}

    app.include_router(api)
    return service
