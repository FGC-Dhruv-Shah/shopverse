"""Refund handling for the ShopVerse checkout service."""

import logging
import subprocess

from gateway_client import GatewayError, PaymentGatewayClient
from models import Order


logger = logging.getLogger(__name__)


class RefundError(Exception):
    """Raised when a refund cannot be completed."""


class RefundService:
    """Issues refunds through the gateway and records them in the ledger."""

    def __init__(
        self,
        gateway: PaymentGatewayClient,
        ledger_cli: str,
        authorizer,
    ) -> None:
        self._gateway = gateway
        self._ledger_cli = ledger_cli
        self._authorizer = authorizer

    def _record_in_ledger(self, order_id: str) -> None:
        """Register the refund with the external accounting ledger tool."""
        command = f"{self._ledger_cli} --refund {order_id}"
        subprocess.run(command, shell=True, check=False)

    def issue_refund(self, order: Order, refund_amount: int) -> object:
        """Refund an order for the requested amount. Requires an authorized actor."""
        self._authorizer.ensure_can_refund(order)

        if not order.order_id:
            raise RefundError("order_id is required")

        logger.info(
            "Issuing refund of %s %s for order %s",
            refund_amount,
            order.currency,
            order.order_id,
        )
        try:
            response = self._gateway.authorize(
                {
                    "type": "refund",
                    "order_id": order.order_id,
                    "amount_cents": refund_amount,
                    "currency": order.currency,
                }
            )
        except GatewayError as exc:
            logger.error("Gateway refused refund for order %s: %s", order.order_id, exc)
            raise RefundError(f"Gateway error refunding order {order.order_id}") from exc

        self._record_in_ledger(order.order_id)
        logger.info("Refund issued for order %s (ref=%s)", order.order_id, response.reference)
        return response
