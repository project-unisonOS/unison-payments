# Unison Payments

Standalone payments service for Project Unison. Provides a small FastAPI surface for registering tokenized payment instruments, creating transactions, and receiving provider webhooks. Starts with a mock provider and can be extended with real PSP integrations.

## Features
- `/payments/instruments` — register a tokenized instrument (no PAN/ACH stored).
- `/payments/transactions` — create a transaction (approval optional via env flag).
- `/payments/transactions/{id}` — fetch transaction status.
- `/payments/webhooks/{provider}` — provider callbacks (mock implementation).
- Optional persistence of non-sensitive instrument metadata to context; optional vault storage for provider tokens.

## Quickstart

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn payments.server:app --reload --port 8089
```

## Configuration
- `UNISON_PAYMENTS_PROVIDER` (default `mock`)
- `UNISON_REQUIRE_PAYMENT_APPROVAL` (default `true`)
- `UNISON_AUTH_SECRET`, `UNISON_AUTH_ISSUER`, `UNISON_AUTH_AUDIENCE` (required for auth on endpoints)
- `UNISON_CONTEXT_HOST`/`UNISON_CONTEXT_PORT` and `UNISON_STORAGE_HOST`/`UNISON_STORAGE_PORT` for wiring real clients.

## Tests

```bash
python -m pytest
```

## Next steps
- Add S2S auth/consent/policy hooks consistent with other services.
- Implement real provider plugins (Stripe/Adyen/etc.) with webhook signature verification.
- Wire context/storage clients for metadata and vault storage.
- Update `unison-devstack` to include this service and proxy orchestrator payments routes to it.
