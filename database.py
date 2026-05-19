"""Lightweight persistence layer for transaction records."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from models import TransactionRecord, TransactionStatus


_SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id     TEXT PRIMARY KEY,
    order_id           TEXT NOT NULL,
    amount_cents       INTEGER NOT NULL,
    currency           TEXT NOT NULL,
    status             TEXT NOT NULL,
    gateway_reference  TEXT,
    created_at         TEXT NOT NULL
);
"""


class TransactionRepository:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        self._ensure_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def save(self, record: TransactionRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO transactions (
                    transaction_id, order_id, amount_cents, currency,
                    status, gateway_reference, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.transaction_id,
                    record.order_id,
                    record.amount_cents,
                    record.currency,
                    record.status.value,
                    record.gateway_reference,
                    record.created_at.isoformat(),
                ),
            )

    def find_by_id(self, transaction_id: str) -> Optional[TransactionRecord]:
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT transaction_id, order_id, amount_cents, currency, "
                "status, gateway_reference, created_at "
                "FROM transactions WHERE transaction_id = ?",
                (transaction_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        from datetime import datetime

        return TransactionRecord(
            transaction_id=row[0],
            order_id=row[1],
            amount_cents=row[2],
            currency=row[3],
            status=TransactionStatus(row[4]),
            gateway_reference=row[5],
            created_at=datetime.fromisoformat(row[6]),
        )
