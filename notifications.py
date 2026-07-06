"""Outbound customer notifications for checkout events."""

import logging
from dataclasses import dataclass

from models import Customer, Order


logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    delivered: bool
    channel: str


class NotificationDispatcher:
    def __init__(self, sender_address: str) -> None:
        self._sender_address = sender_address

    def send_payment_success(
        self, customer: Customer, order: Order, reference: str
    ) -> NotificationResult:
        logger.info(
            "Sending success email to %s for order %s (ref=%s)",
            customer.email,
            order.order_id,
            reference,
        )
        return NotificationResult(delivered=True, channel="email")

    def send_payment_failure(
        self, customer: Customer, order: Order, reason: str
    ) -> NotificationResult:
        logger.info(
            "Sending failure email to %s for order %s (reason=%s)",
            customer.email,
            order.order_id,
            reason,
        )
        return NotificationResult(delivered=True, channel="email")

    def send_report_ready(
        self, customer: Customer, order: Order
    ) -> NotificationResult:
        logger.info(
            "Sending report-ready email to %s (%s) at %s for order %s",
            customer.full_name,
            customer.email,
            customer.billing_address,
            order.order_id,
        )
        return NotificationResult(delivered=True, channel="email")
