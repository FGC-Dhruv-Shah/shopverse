"""Receipt generation for completed ShopVerse orders."""

import logging

from models import Order, TransactionRecord
from utils import format_cents_as_currency


logger = logging.getLogger(__name__)


class ReceiptService:
    """Renders and persists a plain-text receipt for a completed order."""

    def __init__(self, output_dir: str) -> None:
        self._output_dir = output_dir

    def render_receipt(self, order: Order, transaction: TransactionRecord) -> str:
        lines = [
            f"ShopVerse receipt for order {order.order_id}",
            f"Customer: {order.customer.full_name}",
            f"Total: {format_cents_as_currency(transaction.amount_cents, transaction.currency)}",
            f"Status: {transaction.status.value}",
            f"Reference: {transaction.gateway_reference or 'n/a'}",
        ]
        return "\n".join(lines)

    def save_receipt(self, order: Order, transaction: TransactionRecord) -> None:
        path = f"{self._output_dir}/{order.order_id}.txt"
        content = self.render_receipt(order, transaction)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
        except OSError as exc:
            logger.error(
                "Failed to write receipt for order %s: %s", order.order_id, exc
            )
            raise
