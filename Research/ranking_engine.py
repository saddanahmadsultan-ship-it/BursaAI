from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from Research.candidate import Candidate
from Research.confidence_engine import ConfidenceEngine
from Research.consistency_engine import ConsistencyEngine
from Research.ranking_config import RankingWeights
from Research.ranking_models import RankingBreakdown, RankedStrategy
from Research.result import ResearchResult
from Research.robustness_engine import RobustnessEngine
from Research.scoring import clamp, mean, normalize_inverse, normalize_positive


class AIRankingEngine:
    def __init__(
        self,
        weights: Optional[RankingWeights] = None,
        robustness_engine: Optional[RobustnessEngine] = None,
        consistency_engine: Optional[ConsistencyEngine] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
    ) -> None:
        self.weights = weights or RankingWeights()
        self.robustness_engine = robustness_engine or RobustnessEngine()
        self.consistency_engine = consistency_engine or ConsistencyEngine()
        self.confidence_engine = confidence_engine or ConfidenceEngine()

    def rank(
        self,
        items: Iterable[Tuple[Candidate, ResearchResult]],
    ) -> List[RankedStrategy]:
        pairs = list(items)
        peers = [candidate for candidate, _ in pairs]
        ranked: List[RankedStrategy] = []

        for candidate, result in pairs:
            robustness_breakdown = self.robustness_engine.evaluate(
                candidate,
                result,
                peer_candidates=peers,
            )

            consistency_breakdown = self.consistency_engine.evaluate(
                result
            )

            confidence_breakdown = self.confidence_engine.evaluate(
                result,
                robustness_breakdown,
                consistency_breakdown,
            )

            breakdown = self.score(
                candidate,
                result,
                robustness_score=(
                    robustness_breakdown.overall_robustness_score
                ),
                consistency_score=(
                    consistency_breakdown.overall_consistency_score
                ),
                confidence_score=(
                    confidence_breakdown.overall_confidence_score
                ),
            )

            ranked.append(
                RankedStrategy(
                    rank=0,
                    result_id=result.result_id,
                    experiment_id=result.experiment_id,
                    candidate_id=candidate.candidate_id,
                    candidate_hash=candidate.candidate_hash,
                    strategy_name=candidate.strategy_name,
                    candidate_name=candidate.name,
                    parameters=dict(candidate.parameters),
                    breakdown=breakdown,
                    tier=self.classify_tier(
                        breakdown.overall_score
                    ),
                    recommendation=self.recommendation(
                        breakdown.overall_score
                    ),
                    metrics=result.metrics.to_dict(),
                    tags=list(candidate.tags),
                    robustness_breakdown=robustness_breakdown,
                    consistency_breakdown=consistency_breakdown,
                    confidence_breakdown=confidence_breakdown,
                )
            )

        ranked.sort(
            key=lambda item: (
                item.breakdown.overall_score,
                item.breakdown.robustness_score,
                item.breakdown.consistency_score,
                item.breakdown.confidence_score,
                item.breakdown.risk_score,
            ),
            reverse=True,
        )

        for index, item in enumerate(ranked, start=1):
            item.rank = index

        return ranked

    def score(
        self,
        candidate: Candidate,
        result: ResearchResult,
        robustness_score: Optional[float] = None,
        consistency_score: Optional[float] = None,
        confidence_score: Optional[float] = None,
    ) -> RankingBreakdown:
        metrics = result.metrics

        performance_score = mean(
            [
                normalize_positive(metrics.cagr, 30.0),
                normalize_positive(metrics.sharpe_ratio, 2.5),
                normalize_positive(metrics.sortino_ratio, 3.0),
                normalize_positive(metrics.profit_factor, 2.2),
                normalize_positive(metrics.recovery_factor, 4.0),
            ]
        )

        risk_score = mean(
            [
                normalize_inverse(metrics.max_drawdown, 35.0),
                normalize_inverse(metrics.volatility, 45.0),
                normalize_inverse(metrics.exposure, 100.0),
                clamp(metrics.risk_score),
            ]
        )

        resolved_consistency = clamp(
            consistency_score
            if consistency_score is not None
            else metrics.consistency_score
        )

        resolved_robustness = clamp(
            robustness_score
            if robustness_score is not None
            else metrics.robustness_score
        )

        resolved_confidence = clamp(
            confidence_score
            if confidence_score is not None
            else 0.0
        )

        overall_score = (
            performance_score * self.weights.performance
            + risk_score * self.weights.risk
            + resolved_consistency * self.weights.consistency
            + resolved_robustness * self.weights.robustness
            + resolved_confidence * self.weights.confidence
        )

        return RankingBreakdown(
            performance_score=round(performance_score, 4),
            risk_score=round(risk_score, 4),
            consistency_score=round(resolved_consistency, 4),
            robustness_score=round(resolved_robustness, 4),
            confidence_score=round(resolved_confidence, 4),
            overall_score=round(clamp(overall_score), 4),
        )

    @staticmethod
    def classify_tier(score: float) -> str:
        if score >= 90:
            return "RESEARCH_GOLD"
        if score >= 80:
            return "RESEARCH_SILVER"
        if score >= 70:
            return "CANDIDATE"
        if score >= 55:
            return "EXPERIMENTAL"
        return "REJECT"

    @staticmethod
    def recommendation(score: float) -> str:
        mapping: Dict[str, str] = {
            "RESEARCH_GOLD": "PRIORITY_VALIDATION",
            "RESEARCH_SILVER": "ADVANCE_TO_STRESS_TEST",
            "CANDIDATE": "KEEP_FOR_FURTHER_RESEARCH",
            "EXPERIMENTAL": "REVIEW_AND_RETUNE",
            "REJECT": "DO_NOT_ADVANCE",
        }

        return mapping[AIRankingEngine.classify_tier(score)]
