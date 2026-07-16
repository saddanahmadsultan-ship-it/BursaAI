from __future__ import annotations

from typing import Dict, Iterable, List

from Research.pareto_models import ParetoPoint
from Research.ranking_models import RankedStrategy
from Research.tier_gate import TierGate


class PromotionEngine:
    def __init__(self, tier_gate: TierGate | None = None) -> None:
        self.tier_gate = tier_gate or TierGate()

    def evaluate(
        self,
        strategies: Iterable[RankedStrategy],
        pareto_points: Iterable[ParetoPoint],
    ) -> List[Dict]:
        front_by_candidate = {
            point.candidate_id: point.front
            for point in pareto_points
        }

        decisions = []

        for strategy in strategies:
            front = front_by_candidate.get(
                strategy.candidate_id,
                999,
            )

            decision = self.tier_gate.evaluate(
                strategy,
                front,
            )

            decisions.append(
                {
                    "candidate_id": strategy.candidate_id,
                    "candidate_name": strategy.candidate_name,
                    "rank": strategy.rank,
                    "pareto_front": front,
                    "overall_score": (
                        strategy.breakdown.overall_score
                    ),
                    "confidence_score": (
                        strategy.breakdown.confidence_score
                    ),
                    **decision.to_dict(),
                }
            )

        decisions.sort(
            key=lambda item: (
                item["pareto_front"],
                -item["overall_score"],
            )
        )

        return decisions
