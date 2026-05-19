"""HTTP client for the upstream payment gateway."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class GatewayError(Exception):
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class GatewayResponse:
    success: bool
    reference: Optional[str]
    decline_reason: Optional[str]
    raw_payload: Dict[str, Any]


class PaymentGatewayClient:
    def __init__(self, base_url: str, timeout_seconds: int = 15) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()

    def authorize(self, payload: Dict[str, Any]) -> GatewayResponse:
        url = f"{self._base_url}/v1/authorize"
        response = self._session.post(
            url, json=payload, timeout=self._timeout_seconds
        )
        if response.status_code >= 500:
            raise GatewayError(
                f"Gateway unavailable ({response.status_code})",
                code="gateway_unavailable",
            )

        body = response.json()
        return GatewayResponse(
            success=bool(body.get("approved")),
            reference=body.get("reference"),
            decline_reason=body.get("decline_reason"),
            raw_payload=body,
        )

    def close(self) -> None:
        self._session.close()
