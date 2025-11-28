from payments.providers import MockPaymentProvider
from payments.service import PaymentService
from payments.models import PaymentInstrument, PaymentTransactionRequest, PaymentStatus


def test_register_and_create_txn():
    service = PaymentService(MockPaymentProvider())
    instrument = PaymentInstrument(
        instrument_id="inst-1",
        person_id="person-1",
        provider="mock",
        kind="card",
        last4="4242",
    )
    registered = service.register_instrument(instrument, token="tok_123")
    assert registered.instrument_id == "inst-1"
    assert service.get_instrument("inst-1")

    txn_req = PaymentTransactionRequest(
        person_id="person-1",
        instrument_id="inst-1",
        amount=10.5,
        currency="USD",
        description="test purchase",
        authorization_context={"approved": True},
    )
    txn = service.create_transaction(txn_req)
    assert txn.status == PaymentStatus.SUCCEEDED
    assert service.get_transaction_status(txn.txn_id).txn_id == txn.txn_id


def test_webhook_updates_status():
    service = PaymentService(MockPaymentProvider())
    instrument = PaymentInstrument(
        instrument_id="inst-2",
        person_id="person-2",
        provider="mock",
        kind="card",
    )
    service.register_instrument(instrument)
    payload = {
        "txn_id": "txn-1",
        "person_id": "person-2",
        "instrument_id": "inst-2",
        "amount": 5,
        "currency": "USD",
        "status": "succeeded",
    }
    txn = service.process_webhook("mock", payload)
    assert txn.txn_id == "txn-1"
    assert service.get_transaction_status("txn-1").status == PaymentStatus.SUCCEEDED
