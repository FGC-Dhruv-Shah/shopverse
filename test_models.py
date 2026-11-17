"""Unit tests for the ShopVerse domain models (models.py)."""

from datetime import datetime

import pytest

from models import (
    CardDetails,
    Customer,
    LineItem,
    Order,
    TransactionRecord,
    TransactionStatus,
)


def _customer() -> Customer:
    return Customer(
        customer_id="cust-1",
        full_name="Ada Lovelace",
        email="ada@example.com",
        billing_address="1 Analytical Way",
    )


# --------------------------------------------------------------------------- #
# LineItem
# --------------------------------------------------------------------------- #

def test_line_item_total_is_quantity_times_unit_price():
    item = LineItem(sku="sku-1", description="Widget", quantity=3, unit_price_cents=250)
    assert item.total_cents == 750


def test_line_item_total_is_zero_when_quantity_is_zero():
    item = LineItem(sku="sku-1", description="Widget", quantity=0, unit_price_cents=999)
    assert item.total_cents == 0


# --------------------------------------------------------------------------- #
# Order
# --------------------------------------------------------------------------- #

def test_order_total_sums_all_line_items():
    order = Order(
        order_id="ord-1",
        customer=_customer(),
        items=[
            LineItem("sku-1", "Widget", 2, 500),   # 1000
            LineItem("sku-2", "Gadget", 1, 1500),  # 1500
        ],
    )
    assert order.total_cents == 2500


def test_order_total_is_zero_with_no_items():
    order = Order(order_id="ord-2", customer=_customer())
    assert order.items == []
    assert order.total_cents == 0


def test_order_defaults_currency_to_usd_and_sets_created_at():
    order = Order(order_id="ord-3", customer=_customer())
    assert order.currency == "USD"
    assert isinstance(order.created_at, datetime)


def test_order_items_are_independent_between_instances():
    # default_factory must not share one list across orders
    first = Order(order_id="ord-a", customer=_customer())
    second = Order(order_id="ord-b", customer=_customer())
    first.items.append(LineItem("sku-x", "Thing", 1, 100))
    assert first.items and second.items == []


# --------------------------------------------------------------------------- #
# TransactionStatus / TransactionRecord
# --------------------------------------------------------------------------- #

def test_transaction_status_is_a_string_enum():
    assert TransactionStatus.CAPTURED == "captured"
    assert TransactionStatus("refunded") is TransactionStatus.REFUNDED


def test_transaction_record_reference_defaults_to_none():
    record = TransactionRecord(
        transaction_id="txn-1",
        order_id="ord-1",
        amount_cents=2500,
        currency="USD",
        status=TransactionStatus.AUTHORIZED,
    )
    assert record.gateway_reference is None
    assert isinstance(record.created_at, datetime)


def test_card_details_hold_all_fields():
    card = CardDetails(
        cardholder_name="Ada Lovelace",
        card_number="4111111111111111",
        expiry_month=12,
        expiry_year=2030,
        cvv="123",
    )
    assert card.expiry_month == 12
    assert card.card_number.endswith("1111")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
