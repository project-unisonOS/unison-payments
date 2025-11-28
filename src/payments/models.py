from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
import time


class PaymentStatus(str, Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class PaymentInstrument:
    instrument_id: str
    person_id: str
    provider: str
    kind: str
    display_name: str | None = None
    brand: str | None = None
    last4: str | None = None
    expiry: str | None = None
    handle: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())


@dataclass
class PaymentTransactionRequest:
    person_id: str
    instrument_id: str
    amount: float
    currency: str = "USD"
    description: str | None = None
    counterparty: str | None = None
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    provider_token: str | None = None
    surface: str | None = None


@dataclass
class PaymentTransaction:
    txn_id: str
    person_id: str
    instrument_id: str
    amount: float
    currency: str
    status: PaymentStatus
    description: str | None = None
    counterparty: str | None = None
    provider: str | None = None
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())
