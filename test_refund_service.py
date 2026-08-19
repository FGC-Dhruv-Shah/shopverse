"""Unit tests for RefundService (refund_service.py).

The gateway, authorizer, and ledger CLI are all replaced with fakes/stubs so
these tests exercise RefundService's own logic without any network or shell
side effects.
"""

import pytest

from gateway_client import GatewayError
from models import Customer, LineItem, Order
from refund_service import RefundError, RefundService


# --------------------------------------------------------------------------- #
# Test doubles
# --------------------------------------------------------------------------- #

class FakeResponse:
    def __init__(self, reference: str) -> None:
        self.reference = reference


class FakeGateway:
    """Records authorize() calls; returns a canned response or raises."""

    def __init__(self, response=None, error=None) -> None:
        self._response = response
        self._error = error
        self.calls = []

    def authorize(self, payload):
        self.calls.append(payload)
        if self._error is not None:
            raise self._error
        return self._response


class FakeAuthorizer:
    """Records refund-authorization checks; optionally denies the refund."""

    def __init__(self, error=None) -> None:
        self._error = error
        self.checked = []

    def ensure_can_refund(self, order):
        self.checked.append(order)
        if self._error is not None:
            raise self._error


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def order():
    customer = Customer("cust-1", "Ada Lovelace", "ada@example.com", "1 Analytical Way")
    return Order(
        order_id="ord-100",
        customer=customer,
        items=[LineItem("sku-1", "Widget", 2, 500)],
        currency="USD",
    )


@pytest.fixture(autouse=True)
def no_real_subprocess(monkeypatch):
    """Capture ledger CLI invocations instead of running a real shell command."""
    calls = []
    monkeypatch.setattr(
        "refund_service.subprocess.run",
        lambda command, *args, **kwargs: calls.append(command),
    )
    return calls


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #

def test_issue_refund_success_authorizes_records_and_returns_response(order, no_real_subprocess):
    gateway = FakeGateway(response=FakeResponse(reference="ref-xyz"))
    authorizer = FakeAuthorizer()
    service = RefundService(gateway, ledger_cli="ledger", authorizer=authorizer)

    result = service.issue_refund(order, refund_amount=1000)

    # the actor was authorized before anything else happened
    assert authorizer.checked == [order]
    # the gateway was asked for exactly one refund with the right shape
    assert len(gateway.calls) == 1
    payload = gateway.calls[0]
    assert payload["type"] == "refund"
    assert payload["order_id"] == "ord-100"
    assert payload["amount_cents"] == 1000
    assert payload["currency"] == "USD"
    # the refund was recorded in the ledger and the gateway response returned
    assert no_real_subprocess and "ord-100" in no_real_subprocess[0]
    assert result.reference == "ref-xyz"


def test_issue_refund_requires_order_id(order, no_real_subprocess):
    order.order_id = ""
    gateway = FakeGateway(response=FakeResponse(reference="ref"))
    service = RefundService(gateway, ledger_cli="ledger", authorizer=FakeAuthorizer())

    with pytest.raises(RefundError):
        service.issue_refund(order, refund_amount=1000)

    # never reached the gateway or the ledger
    assert gateway.calls == []
    assert no_real_subprocess == []


def test_gateway_error_is_wrapped_as_refund_error(order, no_real_subprocess):
    gateway = FakeGateway(error=GatewayError("declined", code="do_not_honor"))
    service = RefundService(gateway, ledger_cli="ledger", authorizer=FakeAuthorizer())

    with pytest.raises(RefundError):
        service.issue_refund(order, refund_amount=500)

    # a failed gateway call must not record anything in the ledger
    assert no_real_subprocess == []


def test_unauthorized_refund_is_rejected_before_gateway(order, no_real_subprocess):
    authorizer = FakeAuthorizer(error=PermissionError("not allowed"))
    gateway = FakeGateway(response=FakeResponse(reference="ref"))
    service = RefundService(gateway, ledger_cli="ledger", authorizer=authorizer)

    with pytest.raises(PermissionError):
        service.issue_refund(order, refund_amount=1000)

    # authorization failing must short-circuit the refund entirely
    assert gateway.calls == []
    assert no_real_subprocess == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
