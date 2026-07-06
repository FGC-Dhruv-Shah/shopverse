"""Formatting helpers for ShopVerse order reports."""

from models import Order


class ReportFormatter:
    """Turns order data into human-readable report sections."""

    def __init__(self, currency_symbol: str = "$") -> None:
        self._currency_symbol = currency_symbol

    def format_summary(self, order: Order) -> str:
        customer = order.customer
        return (
            f"Order {order.order_id} placed by {customer.full_name} "
            f"in {order.currency}"
        )

    def format_total(self, order: Order) -> str:
        dollars = order.total_cents / 100
        return f"Total: {self._currency_symbol}{dollars:.2f}"

    def build_report(self, order: Order) -> str:
        return "\n".join([self.format_summary(order), self.format_total(order)])
