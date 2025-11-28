from __future__ import annotations

import uuid
from typing import Dict, Any

from .models import PaymentInstrument, PaymentTransaction, PaymentTransactionRequest, PaymentStatus


class PaymentProvider:
    """Provider interface for payment operations."""

    name: str = "mock"

    def register_instrument(self, instrument: PaymentInstrument) -> PaymentInstrument:  # pragma: no cover - interface
        raise NotImplementedError

    def create_transaction(self, request: PaymentTransactionRequest) -> PaymentTransaction:  # pragma: no cover - interface
        raise NotImplementedError

    def get_status(self, txn_id: str) -> PaymentTransaction:  # pragma: no cover - interface
        raise NotImplementedError

    def handle_webhook(self, payload: Dict[str, Any]) -> PaymentTransaction:  # pragma: no cover - interface
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    """In-memory provider for dev/test flows."""

    name = "mock"

    def __init__(self):
        self._transactions: Dict[str, PaymentTransaction] = {}

    def register_instrument(self, instrument: PaymentInstrument) -> PaymentInstrument:
        # No-op; return as-is
        return instrument

    def create_transaction(self, request: PaymentTransactionRequest) -> PaymentTransaction:
        txn_id = str(uuid.uuid4())
        txn = PaymentTransaction(
            txn_id=txn_id,
            person_id=request.person_id,
            instrument_id=request.instrument_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.SUCCEEDED,
            description=request.description,
            counterparty=request.counterparty,
            provider=self.name,
            authorization_context=request.authorization_context,
        )
        self._transactions[txn_id] = txn
        return txn

    def get_status(self, txn_id: str) -> PaymentTransaction:
        if txn_id not in self._transactions:
            raise KeyError("transaction not found")
        return self._transactions[txn_id]

    def handle_webhook(self, payload: Dict[str, Any]) -> PaymentTransaction:
        # Mock provider trusts incoming payload; real providers should verify signature.
        txn_id = payload.get("txn_id") or str(uuid.uuid4())
        status = payload.get("status") or PaymentStatus.SUCCEEDED
        txn = PaymentTransaction(
            txn_id=txn_id,
            person_id=payload.get("person_id", "unknown"),
            instrument_id=payload.get("instrument_id", "unknown"),
            amount=float(payload.get("amount", 0)),
            currency=payload.get("currency", "USD"),
            status=PaymentStatus(status) if isinstance(status, str) else status,
            description=payload.get("description"),
            counterparty=payload.get("counterparty"),
            provider=self.name,
        )
        self._transactions[txn_id] = txn
        return txn
