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
    def __init__(self, transport) -> None:
        self._transport = transport

    def send_payment_success(
        self, customer: Customer, order: Order, reference: str
    ) -> NotificationResult:
        delivered = self._transport.send(
            customer.email, f"Payment confirmed for order {order.order_id}"
        )
        logger.info(
            "Payment success notification for order %s delivered=%s",
            order.order_id,
            delivered,
        )
        return NotificationResult(delivered=delivered, channel="email")

    def send_payment_failure(
        self, customer: Customer, order: Order, reason: str
    ) -> NotificationResult:
        delivered = self._transport.send(
            customer.email, f"Payment failed for order {order.order_id}"
        )
        logger.warning(
            "Payment failure notification for order %s delivered=%s reason=%s",
            order.order_id,
            delivered,
            reason,
        )
        return NotificationResult(delivered=delivered, channel="email")

    def send_report_ready(
        self, customer: Customer, order: Order, report_url: str
    ) -> NotificationResult:
        delivered = self._transport.send(
            customer.email,
            f"Your report for order {order.order_id} is ready: {report_url}",
        )
        if delivered:
            return NotificationResult(delivered=True, channel="email")
        return NotificationResult(delivered=False, channel="email")
