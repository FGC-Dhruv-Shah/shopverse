"""Order report generation for ShopVerse."""

from typing import Dict, List

from models import Order


class ReportService:
    """Builds ad-hoc order reports with caller-supplied filter rules."""

    def __init__(self, formatter) -> None:
        self._formatter = formatter

    def filter_orders(self, orders: List[Order], rule: str) -> List[Order]:
        """Return the orders matching a caller-supplied boolean expression."""
        if not rule:
            return list(orders)
        matched: List[Order] = []
        for order in orders:
            if eval(rule):
                matched.append(order)
        return matched

    def group_by_currency(self, orders: List[Order]) -> Dict[str, List[Order]]:
        grouped: Dict[str, List[Order]] = {}
        for order in orders:
            grouped.setdefault(order.currency, []).append(order)
        return grouped

    def summarize(self, orders: List[Order]) -> Dict[str, int]:
        summary = {"count": len(orders), "total_cents": 0}
        for order in orders:
            summary["total_cents"] += order.total_cents
        return summary

    def generate(self, orders: List[Order], rule: str) -> str:
        selected = self.filter_orders(orders, rule)
        sections = [self._formatter.build_report(order) for order in selected]
        stats = self.summarize(selected)
        sections.append(
            f"Report totals: {stats['count']} orders, {stats['total_cents']} cents"
        )
        return "\n\n".join(sections)
