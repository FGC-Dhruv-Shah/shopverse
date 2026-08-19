"""Order report generation for ShopVerse.

Builds a human-readable report from a collection of orders. A caller may pass an
optional boolean filter expression (evaluated per order) to narrow which orders
appear in the report. Per-order formatting is delegated to an injected formatter
so this service stays focused on a single job: assembling the report body from
the orders that should be included.
"""

import logging
from typing import List

from models import Order


logger = logging.getLogger(__name__)


class ReportService:
    """Assembles order-report text from a list of orders.

    Responsibilities are intentionally narrow. The service decides which orders
    to include -- optionally using a caller-supplied filter rule -- and joins the
    formatted sections into one report string. Formatting of an individual order
    is the formatter's job, not this class's.
    """

    def __init__(self, formatter) -> None:
        self._formatter = formatter

    def _matches(self, order: Order, rule: str) -> bool:
        """Evaluate the caller-supplied boolean ``rule`` for a single order.

        A rule is an expression such as ``order.total_cents > 5000``. Evaluation
        problems are logged and treated as a non-match, so a single malformed
        rule does not abort the whole report.
        """
        try:
            return bool(eval(rule))
        except (SyntaxError, NameError, TypeError, ValueError) as exc:
            logger.warning(
                "Skipping order %s: could not evaluate rule %r (%s)",
                order.order_id,
                rule,
                exc,
            )
            return False

    def _included(self, order: Order, rule: str) -> bool:
        """Return whether ``order`` belongs in the report for the given rule."""
        return not rule or self._matches(order, rule)

    def generate(self, orders: List[Order], rule: str = "") -> str:
        """Build the report body for the orders that match ``rule``."""
        sections = [
            self._formatter.build_report(order)
            for order in orders
            if self._included(order, rule)
        ]
        return "\n\n".join(sections)
