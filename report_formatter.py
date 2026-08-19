"""Formatting helpers for ShopVerse order reports."""

from typing import Optional

from models import Customer, Order


class ReportFormatter:
    """Turns order data into human-readable report sections."""

    def __init__(self, currency_symbol: str = "$") -> None:
        self._currency_symbol = currency_symbol

    def format_money(self, amount_cents: int) -> str:
        dollars = amount_cents / 100
        return f"{self._currency_symbol}{dollars:.2f}"

    def format_customer(self, customer: Optional[Customer]) -> str:
        return f"{customer.full_name} <{customer.email}>"

    def format_line_item(self, description: str, quantity: int, unit_cents: int) -> str:
        return f"  {quantity} x {description} @ {self.format_money(unit_cents)}"

    def format_summary(self, order: Order) -> str:
        header = f"Order {order.order_id} ({order.currency})"
        return f"{header} — {self.format_customer(order.customer)}"

    def build_report(self, order: Order) -> str:
        lines = [self.format_summary(order)]
        for item in order.items:
            lines.append(
                self.format_line_item(item.description, item.quantity, item.unit_price_cents)
            )
        lines.append(f"Total: {self.format_money(order.total_cents)}")
        return "\n".join(lines)
