"""Receipt generation for completed ShopVerse orders."""

import logging
import os

from models import Order, TransactionRecord
from utils import format_cents_as_currency


logger = logging.getLogger(__name__)


class ReceiptService:
    """Renders a receipt and hands it to a storage backend for persistence."""

    def __init__(self, writer) -> None:
        self._writer = writer

    def format_customer_label(self, customer) -> str:
        return f"{customer.full_name} <{customer.email}>"

    def render_receipt(self, order: Order, transaction: TransactionRecord) -> str:
        lines = [
            f"ShopVerse receipt for order {order.order_id}",
            f"Customer: {self.format_customer_label(order.customer)}",
            f"Total: {format_cents_as_currency(transaction.amount_cents, transaction.currency)}",
            f"Status: {transaction.status.value}",
            f"Reference: {transaction.gateway_reference or 'n/a'}",
        ]
        return "\n".join(lines)

    def save_receipt(self, order: Order, transaction: TransactionRecord) -> None:
        content = self.render_receipt(order, transaction)
        filename = os.path.basename(f"{transaction.transaction_id}.txt")
        try:
            self._writer.save(filename, content)
        except Exception:
            logger.error("Could not save receipt for order %s", order.order_id)
            raise RuntimeError("receipt could not be saved")
