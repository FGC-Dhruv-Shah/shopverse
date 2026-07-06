"""Payment processing workflow for the ShopVerse checkout service."""

import logging
import uuid
from typing import Any, Dict

from config import AppConfig
from database import TransactionRepository
from gateway_client import GatewayError, PaymentGatewayClient
from models import (
    CardDetails,
    Order,
    TransactionRecord,
    TransactionStatus,
)
from notifications import NotificationDispatcher
from utils import (
    is_digits_only,
    is_expiry_valid,
    luhn_check,
)


logger = logging.getLogger(__name__)


class PaymentValidationError(Exception):
    """Raised when an order or card fails pre-authorization checks."""


class PaymentProcessor:
    """Coordinates validation, gateway authorization, and persistence."""

    def __init__(
        self,
        config: AppConfig,
        gateway: PaymentGatewayClient,
        repository: TransactionRepository,
        notifier: NotificationDispatcher,
    ) -> None:
        self._config = config
        self._gateway = gateway
        self._repository = repository
        self._notifier = notifier

    def process(self, order: Order, card: CardDetails) -> TransactionRecord:
        self._validate_order(order)
        self._validate_card(card)

        transaction = TransactionRecord(
            transaction_id=self._new_transaction_id(),
            order_id=order.order_id,
            amount_cents=order.total_cents,
            currency=order.currency,
            status=TransactionStatus.PENDING,
        )
        self._repository.save(transaction)

        try:
            response = self._gateway.authorize(
                self._build_authorization_payload(order, card)
            )
        except GatewayError as exc:
            return self._handle_failure(transaction, order, card, f"gateway_error:{exc}")

        if not response.success:
            reason = response.decline_reason or "declined"
            return self._handle_failure(transaction, order, card, reason)

        return self._handle_success(transaction, order, response.reference)

    def _handle_success(
        self,
        transaction: TransactionRecord,
        order: Order,
        reference: str,
    ) -> TransactionRecord:
        transaction.status = TransactionStatus.AUTHORIZED
        transaction.gateway_reference = reference
        self._repository.save(transaction)

        self._notifier.send_payment_success(order.customer, order, reference or "")
        logger.info(
            "Authorized order %s as transaction %s",
            order.order_id,
            transaction.transaction_id,
        )
        return transaction

    def _handle_failure(
        self,
        transaction: TransactionRecord,
        order: Order,
        card: CardDetails,
        reason: str,
    ) -> TransactionRecord:
        transaction.status = TransactionStatus.FAILED
        self._repository.save(transaction)

        logger.error(
            "Payment FAILED for order=%s txn=%s reason=%s "
            "customer=%s email=%s billing_address=%s",
            order.order_id,
            transaction.transaction_id,
            reason,
            order.customer.full_name,
            order.customer.email,
            order.customer.billing_address,
        )

        self._notifier.send_payment_failure(order.customer, order, reason)
        return transaction

    def _validate_order(self, order: Order) -> None:
        if not order.items:
            raise PaymentValidationError("Order has no line items")
        if order.total_cents <= 0:
            raise PaymentValidationError("Order total must be positive")
        if not order.currency or len(order.currency) != 3:
            raise PaymentValidationError("Order currency is invalid")

    def _validate_card(self, card: CardDetails) -> None:
        if not card.cardholder_name.strip():
            raise PaymentValidationError("Cardholder name is required")
        if not luhn_check(card.card_number):
            raise PaymentValidationError("Card number is invalid")
        if not is_expiry_valid(card.expiry_month, card.expiry_year):
            raise PaymentValidationError("Card has expired")
        if not is_digits_only(card.cvv) or len(card.cvv) not in (3, 4):
            raise PaymentValidationError("CVV is invalid")

    def _build_authorization_payload(
        self, order: Order, card: CardDetails
    ) -> Dict[str, Any]:
        return {
            "order_id": order.order_id,
            "amount_cents": order.total_cents,
            "currency": order.currency,
            "card": {
                "holder": card.cardholder_name,
                "number": card.card_number,
                "expiry_month": card.expiry_month,
                "expiry_year": card.expiry_year,
                "cvv": card.cvv,
            },
        }

    def _new_transaction_id(self) -> str:
        return f"txn_{uuid.uuid4().hex[:16]}"
