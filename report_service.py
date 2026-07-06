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

    def sort_orders(self, orders: List[Order], key: str = "total") -> List[Order]:
        if key == "total":
            return sorted(orders, key=lambda o: o.total_cents, reverse=True)
        if key == "date":
            return sorted(orders, key=lambda o: o.created_at)
        return list(orders)

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

    def _render_section(self, title: str, orders: List[Order]) -> str:
        lines = [f"== {title} =="]
        for order in orders:
            lines.append(self._formatter.build_report(order))
        return "\n".join(lines)

    def generate(self, orders: List[Order], rule: str = "") -> str:
        selected = self.filter_orders(orders, rule)
        selected = self.sort_orders(selected, key="total")
        sections: List[str] = []
        for currency, group in self.group_by_currency(selected).items():
            sections.append(self._render_section(f"Orders in {currency}", group))
        stats = self.summarize(selected)
        sections.append(
            f"Totals: {stats['count']} orders, {stats['total_cents']} cents"
        )
        return "\n\n".join(sections)
