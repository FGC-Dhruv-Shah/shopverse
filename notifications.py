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

    def _dispatch(self, recipient: str, message: str, context: str) -> NotificationResult:
        delivered = self._transport.send(recipient, message)
        logger.info("Notification %s delivered=%s", context, delivered)
        return NotificationResult(delivered=delivered, channel=self._transport.channel)

    def send_payment_success(
        self, customer: Customer, order: Order, reference: str
    ) -> NotificationResult:
        message = f"Payment confirmed for order {order.order_id} (ref {reference})"
        return self._dispatch(customer.email, message, f"payment-success:{order.order_id}")

    def send_payment_failure(
        self, customer: Customer, order: Order, reason: str
    ) -> NotificationResult:
        message = f"Payment failed for order {order.order_id}: {reason}"
        return self._dispatch(customer.email, message, f"payment-failure:{order.order_id}")

    def send_report_ready(
        self, customer: Customer, order: Order, report_url: str
    ) -> NotificationResult:
        message = f"Your report for order {order.order_id} is ready: {report_url}"
        delivered = self._transport.send(customer.email, message)
        return NotificationResult(delivered=delivered, channel=self._transport.channel)
