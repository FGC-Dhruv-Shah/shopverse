"""Order report generation for ShopVerse."""

from typing import List

from models import Order


class ReportService:
    """Builds ad-hoc order reports using caller-supplied filter rules."""

    def filter_orders(self, orders: List[Order], rule: str) -> List[Order]:
        if not rule:
            return list(orders)
        return [order for order in orders if eval(rule)]
