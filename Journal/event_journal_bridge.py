"""
=========================================================
BursaAI Event to Journal Bridge
Version : 6.0 Sprint 6D
=========================================================
"""

from __future__ import annotations

from typing import Dict

from Framework.event_bus import Event, EventBus
from Journal.journal_models import (
    JournalEvent,
    JournalRecord,
)
from Journal.trade_journal import TradeJournal


class EventJournalBridge:
    """
    Subscribes to BursaAI events and writes records automatically.
    """

    EVENT_MAP = {
        "DecisionCompleted": JournalEvent.DECISION,
        "PaperOrderUpdated": JournalEvent.ORDER,
        "PortfolioAllocated": JournalEvent.PORTFOLIO,
        "ExecutionStarted": JournalEvent.EXECUTION,
        "ExecutionCompleted": JournalEvent.EXECUTION,
        "ExecutionFailed": JournalEvent.ERROR,
        "StrategyGenerated": JournalEvent.SIGNAL,
        "PositionCalculated": JournalEvent.POSITION,
    }

    def __init__(
        self,
        event_bus: EventBus,
        journal: TradeJournal,
    ):
        self.event_bus = event_bus
        self.journal = journal
        self._attached = False

    def attach(self) -> None:
        if self._attached:
            return

        for event_name in self.EVENT_MAP:
            self.event_bus.subscribe(
                event_name,
                self._handle,
            )

        self._attached = True

    def detach(self) -> None:
        if not self._attached:
            return

        for event_name in self.EVENT_MAP:
            self.event_bus.unsubscribe(
                event_name,
                self._handle,
            )

        self._attached = False

    def _handle(self, event: Event) -> None:
        payload = (
            event.payload
            if isinstance(event.payload, dict)
            else {"payload": event.payload}
        )

        record = self._build_record(
            event.name,
            payload,
        )

        self.journal.add(record)

    def _build_record(
        self,
        event_name: str,
        payload: Dict,
    ) -> JournalRecord:
        event_type = self.EVENT_MAP[
            event_name
        ]

        symbol = str(
            payload.get(
                "symbol",
                "",
            )
        )

        action = str(
            payload.get(
                "side",
                payload.get(
                    "recommendation",
                    payload.get(
                        "strategy",
                        "",
                    ),
                ),
            )
        )

        quantity = int(
            payload.get(
                "filled_shares",
                payload.get(
                    "shares",
                    0,
                ),
            )
            or 0
        )

        price = float(
            payload.get(
                "filled_price",
                payload.get(
                    "price",
                    payload.get(
                        "entry",
                        0,
                    ),
                ),
            )
            or 0
        )

        pnl = float(
            payload.get(
                "pnl",
                payload.get(
                    "realized_pnl",
                    0,
                ),
            )
            or 0
        )

        score = float(
            payload.get(
                "score",
                payload.get(
                    "average_score",
                    0,
                ),
            )
            or 0
        )

        confidence = float(
            payload.get(
                "confidence",
                payload.get(
                    "average_confidence",
                    0,
                ),
            )
            or 0
        )

        signal = str(
            payload.get(
                "signal",
                payload.get(
                    "recommendation",
                    payload.get(
                        "strategy",
                        "",
                    ),
                ),
            )
        )

        status = str(
            payload.get(
                "status",
                event_name,
            )
        )

        notes = str(
            payload.get(
                "summary",
                payload.get(
                    "reason",
                    payload.get(
                        "error",
                        "",
                    ),
                ),
            )
        )

        return JournalRecord(
            event_type=event_type,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            pnl=pnl,
            score=score,
            confidence=confidence,
            signal=signal,
            status=status,
            notes=notes,
            run_id=str(
                payload.get(
                    "run_id",
                    "",
                )
            ),
            metadata={
                "event_name": event_name,
                "source": "",
                "payload": payload,
            },
        )
