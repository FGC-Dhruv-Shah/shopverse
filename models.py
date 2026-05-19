"""Domain models for the ShopVerse checkout service."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TransactionStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Customer:
    customer_id: str
    full_name: str
    email: str
    billing_address: str


@dataclass
class LineItem:
    sku: str
    description: str
    quantity: int
    unit_price_cents: int

    @property
    def total_cents(self) -> int:
        return self.quantity * self.unit_price_cents


@dataclass
class Order:
    order_id: str
    customer: Customer
    items: List[LineItem] = field(default_factory=list)
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_cents(self) -> int:
        return sum(item.total_cents for item in self.items)


@dataclass
class CardDetails:
    cardholder_name: str
    card_number: str
    expiry_month: int
    expiry_year: int
    cvv: str


@dataclass
class TransactionRecord:
    transaction_id: str
    order_id: str
    amount_cents: int
    currency: str
    status: TransactionStatus
    gateway_reference: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
