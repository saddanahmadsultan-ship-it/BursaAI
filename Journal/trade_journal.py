"""
=========================================================
BursaAI SQLite Trade Journal
Version : 6.0 Sprint 6D Fix 1
=========================================================
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from Journal.journal_models import (
    JournalEvent,
    JournalRecord,
)


class TradeJournal:
    """
    Persistent SQLite journal for signals, decisions, orders,
    trades, positions, portfolio events and execution sessions.

    Windows-safe:
    Every SQLite connection is explicitly closed using
    contextlib.closing().
    """

    def __init__(
        self,
        database_path: str = "Data/bursaai_journal.db",
    ):
        self.database_path = Path(database_path)

        if str(self.database_path) != ":memory:":
            self.database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            str(self.database_path),
            timeout=30.0,
        )

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_records (
                    record_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    symbol TEXT,
                    action TEXT,
                    quantity INTEGER,
                    price REAL,
                    pnl REAL,
                    score REAL,
                    confidence REAL,
                    signal TEXT,
                    status TEXT,
                    notes TEXT,
                    run_id TEXT,
                    metadata_json TEXT
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_journal_symbol
                ON journal_records(symbol)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_journal_event
                ON journal_records(event_type)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_journal_created
                ON journal_records(created_at)
                """
            )

            connection.commit()

    def add(
        self,
        record: JournalRecord,
    ) -> str:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO journal_records (
                    record_id,
                    created_at,
                    event_type,
                    symbol,
                    action,
                    quantity,
                    price,
                    pnl,
                    score,
                    confidence,
                    signal,
                    status,
                    notes,
                    run_id,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.created_at,
                    record.event_type.value,
                    record.symbol,
                    record.action,
                    int(record.quantity),
                    float(record.price),
                    float(record.pnl),
                    float(record.score),
                    float(record.confidence),
                    record.signal,
                    record.status,
                    record.notes,
                    record.run_id,
                    json.dumps(
                        record.metadata,
                        ensure_ascii=False,
                        default=str,
                    ),
                ),
            )

            connection.commit()

        return record.record_id

    def add_many(
        self,
        records: Iterable[JournalRecord],
    ) -> int:
        count = 0

        with closing(self._connect()) as connection:
            for record in records:
                connection.execute(
                    """
                    INSERT INTO journal_records (
                        record_id,
                        created_at,
                        event_type,
                        symbol,
                        action,
                        quantity,
                        price,
                        pnl,
                        score,
                        confidence,
                        signal,
                        status,
                        notes,
                        run_id,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.record_id,
                        record.created_at,
                        record.event_type.value,
                        record.symbol,
                        record.action,
                        int(record.quantity),
                        float(record.price),
                        float(record.pnl),
                        float(record.score),
                        float(record.confidence),
                        record.signal,
                        record.status,
                        record.notes,
                        record.run_id,
                        json.dumps(
                            record.metadata,
                            ensure_ascii=False,
                            default=str,
                        ),
                    ),
                )

                count += 1

            connection.commit()

        return count

    def list_records(
        self,
        *,
        symbol: Optional[str] = None,
        event_type: Optional[JournalEvent] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if symbol:
            clauses.append("symbol = ?")
            params.append(str(symbol))

        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type.value)

        where = (
            " WHERE " + " AND ".join(clauses)
            if clauses
            else ""
        )

        query = (
            """
            SELECT
                record_id,
                created_at,
                event_type,
                symbol,
                action,
                quantity,
                price,
                pnl,
                score,
                confidence,
                signal,
                status,
                notes,
                run_id,
                metadata_json
            FROM journal_records
            """
            + where
            + """
            ORDER BY created_at DESC
            LIMIT ?
            """
        )

        params.append(max(int(limit), 1))

        with closing(self._connect()) as connection:
            rows = connection.execute(
                query,
                params,
            ).fetchall()

        output = []

        for row in rows:
            output.append(
                {
                    "record_id": row[0],
                    "created_at": row[1],
                    "event_type": row[2],
                    "symbol": row[3],
                    "action": row[4],
                    "quantity": row[5],
                    "price": row[6],
                    "pnl": row[7],
                    "score": row[8],
                    "confidence": row[9],
                    "signal": row[10],
                    "status": row[11],
                    "notes": row[12],
                    "run_id": row[13],
                    "metadata": json.loads(
                        row[14] or "{}"
                    ),
                }
            )

        return output

    def count(self) -> int:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM journal_records
                """
            ).fetchone()

        return int(row[0])

    def summary(self) -> Dict[str, Any]:
        with closing(self._connect()) as connection:
            total = connection.execute(
                "SELECT COUNT(*) FROM journal_records"
            ).fetchone()[0]

            realized = connection.execute(
                """
                SELECT COALESCE(SUM(pnl), 0)
                FROM journal_records
                WHERE event_type IN ('TRADE', 'ORDER')
                """
            ).fetchone()[0]

            winners = connection.execute(
                """
                SELECT COUNT(*)
                FROM journal_records
                WHERE pnl > 0
                """
            ).fetchone()[0]

            losers = connection.execute(
                """
                SELECT COUNT(*)
                FROM journal_records
                WHERE pnl < 0
                """
            ).fetchone()[0]

        return {
            "records": int(total),
            "realized_pnl": round(
                float(realized or 0),
                2,
            ),
            "winning_records": int(winners),
            "losing_records": int(losers),
        }

    def clear(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                "DELETE FROM journal_records"
            )
            connection.commit()

    def close(self) -> None:
        """
        Compatibility hook.

        Connections are already closed after every operation,
        so no persistent resource remains open.
        """
        return None
