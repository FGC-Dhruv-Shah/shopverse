"""Order report generation and export for ShopVerse."""

import logging
import subprocess

from models import Order


logger = logging.getLogger(__name__)


class ReportService:
    """Builds order reports and exports them via an external renderer."""

    def __init__(self, renderer_cli: str) -> None:
        self._renderer_cli = renderer_cli

    def build_header(self, customer) -> str:
        return f"Report for {customer.full_name} <{customer.email}>"

    def log_report_request(self, order: Order) -> None:
        logger.info(
            "Report requested: order=%s customer=%s email=%s address=%s",
            order.order_id,
            order.customer.full_name,
            order.customer.email,
            order.customer.billing_address,
        )

    def export_pdf(self, order_id: str) -> None:
        if not order_id:
            raise ValueError("order_id is required")
        command = f"{self._renderer_cli} --order {order_id}"
        subprocess.run(command, shell=True, check=False)
