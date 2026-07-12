"""
=========================================================
BursaAI Paper Order
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class PaperOrder:
    symbol: str
    side: OrderSide
    shares: int
    price: float
    order_id: str = field(
        default_factory=lambda: uuid4().hex[:12]
    )
    status: OrderStatus = OrderStatus.PENDING
    filled_price: float = 0.0
    filled_shares: int = 0
    commission: float = 0.0
    reason: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    filled_at: Optional[str] = None

    @property
    def gross_value(self) -> float:
        return round(
            max(self.shares, 0) * max(self.price, 0.0),
            2,
        )

    def fill(
        self,
        filled_price: float,
        filled_shares: Optional[int] = None,
        commission: float = 0.0,
    ) -> None:
        self.filled_price = max(float(filled_price), 0.0)
        self.filled_shares = (
            self.shares
            if filled_shares is None
            else max(int(filled_shares), 0)
        )
        self.commission = max(float(commission), 0.0)
        self.status = OrderStatus.FILLED
        self.filled_at = datetime.now(
            timezone.utc
        ).isoformat()

    def reject(self, reason: str) -> None:
        self.status = OrderStatus.REJECTED
        self.reason = str(reason)
