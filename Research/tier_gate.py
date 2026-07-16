from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from Research.ranking_models import RankedStrategy


@dataclass
class TierGateDecision:
    approved_tier: str
    passed: bool
    action: str
    reasons: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved_tier": self.approved_tier,
            "passed": self.passed,
            "action": self.action,
            "reasons": list(self.reasons),
        }


class TierGate:
    def evaluate(
        self,
        strategy: RankedStrategy,
        pareto_front: int,
    ) -> TierGateDecision:
        score = strategy.breakdown.overall_score
        robustness = strategy.breakdown.robustness_score
        consistency = strategy.breakdown.consistency_score
        confidence = strategy.breakdown.confidence_score
        risk = strategy.breakdown.risk_score

        reasons: list[str] = []

        if (
            score >= 88
            and robustness >= 82
            and consistency >= 82
            and confidence >= 80
            and risk >= 65
            and pareto_front == 1
        ):
            return TierGateDecision(
                approved_tier="RESEARCH_GOLD",
                passed=True,
                action="PROMOTE_TO_PAPER_TRADING",
                reasons=["All Gold gates passed."],
            )

        if (
            score >= 78
            and robustness >= 75
            and consistency >= 75
            and confidence >= 70
            and risk >= 55
            and pareto_front <= 2
        ):
            return TierGateDecision(
                approved_tier="RESEARCH_SILVER",
                passed=True,
                action="ADVANCE_TO_STRESS_TEST",
                reasons=["All Silver gates passed."],
            )

        if (
            score >= 68
            and robustness >= 65
            and consistency >= 65
            and confidence >= 60
            and pareto_front <= 3
        ):
            return TierGateDecision(
                approved_tier="CANDIDATE",
                passed=True,
                action="KEEP_FOR_FURTHER_RESEARCH",
                reasons=["Candidate gates passed."],
            )

        if score >= 50:
            if robustness < 65:
                reasons.append("Robustness below Candidate threshold.")
            if consistency < 65:
                reasons.append("Consistency below Candidate threshold.")
            if confidence < 60:
                reasons.append("Confidence below Candidate threshold.")
            if pareto_front > 3:
                reasons.append("Pareto front too weak.")

            return TierGateDecision(
                approved_tier="EXPERIMENTAL",
                passed=False,
                action="REVIEW_AND_RETUNE",
                reasons=reasons or ["Experimental only."],
            )

        return TierGateDecision(
            approved_tier="REJECT",
            passed=False,
            action="DO_NOT_ADVANCE",
            reasons=["Overall score below minimum gate."],
        )
