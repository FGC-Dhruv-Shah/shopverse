"""Runtime configuration for the ShopVerse checkout service."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    environment: str
    database_url: str
    gateway_base_url: str
    log_level: str
    request_timeout_seconds: int


def load_config() -> AppConfig:
    return AppConfig(
        environment=os.getenv("SHOPVERSE_ENV", "development"),
        database_url=os.getenv("SHOPVERSE_DB_URL", "sqlite:///shopverse.db"),
        gateway_base_url=os.getenv(
            "SHOPVERSE_GATEWAY", "https://gateway.example.com"
        ),
        log_level=os.getenv("SHOPVERSE_LOG_LEVEL", "INFO"),
        request_timeout_seconds=int(os.getenv("SHOPVERSE_TIMEOUT", "15")),
    )
