from __future__ import annotations

from TradingIntelligence.position_contracts import PositionCandidate


class EntryPriceEngine:
    @staticmethod
    def calculate(candidate: PositionCandidate) -> float:
        if candidate.preferred_entry and candidate.preferred_entry > 0:
            return round(float(candidate.preferred_entry), 4)

        entry = float(candidate.price)

        if (
            candidate.support_price
            and candidate.support_price > 0
            and candidate.support_price <= candidate.price
        ):
            support_gap = candidate.price - candidate.support_price
            if support_gap <= max(candidate.atr, candidate.price * 0.02):
                entry = (
                    candidate.price * 0.65
                    + candidate.support_price * 0.35
                )

        return round(max(entry, 0.0001), 4)
