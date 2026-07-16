from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Set


@dataclass
class LabelBuilderConfig:
    positive_actions: Set[str] | None = None
    positive_tiers: Set[str] | None = None
    minimum_score: float = 78.0
    minimum_confidence: float = 70.0

    def __post_init__(self) -> None:
        if self.positive_actions is None:
            self.positive_actions = {
                "PROMOTE_TO_PAPER_TRADING",
                "ADVANCE_TO_STRESS_TEST",
            }

        if self.positive_tiers is None:
            self.positive_tiers = {
                "RESEARCH_GOLD",
                "RESEARCH_SILVER",
            }


class ResearchLabelBuilder:
    def __init__(
        self,
        config: LabelBuilderConfig | None = None,
    ) -> None:
        self.config = config or LabelBuilderConfig()

    def build(self, record: Dict[str, Any]) -> float:
        action = str(
            record.get("promotion_action", "")
        ).upper()

        tier = str(
            record.get("approved_tier")
            or record.get("tier", "")
        ).upper()

        overall_score = float(
            record.get("overall_score", 0.0)
        )

        confidence_score = float(
            record.get("confidence_score", 0.0)
        )

        action_pass = action in self.config.positive_actions
        tier_pass = tier in self.config.positive_tiers
        score_pass = (
            overall_score >= self.config.minimum_score
            and confidence_score >= self.config.minimum_confidence
        )

        return 1.0 if action_pass or tier_pass or score_pass else 0.0
