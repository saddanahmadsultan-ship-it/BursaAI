"""
=========================================================
BursaAI Journal Models
Version : 6.0 Sprint 6D
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class JournalEvent(str, Enum):
    SIGNAL = "SIGNAL"
    DECISION = "DECISION"
    ORDER = "ORDER"
    TRADE = "TRADE"
    POSITION = "POSITION"
    PORTFOLIO = "PORTFOLIO"
    EXECUTION = "EXECUTION"
    ERROR = "ERROR"


@dataclass(slots=True)
class JournalRecord:
    event_type: JournalEvent
    symbol: str = ""
    action: str = ""
    quantity: int = 0
    price: float = 0.0
    pnl: float = 0.0
    score: float = 0.0
    confidence: float = 0.0
    signal: str = ""
    status: str = ""
    notes: str = ""
    run_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    record_id: str = field(
        default_factory=lambda: uuid4().hex[:16]
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
