from __future__ import annotations

from statistics import mean
from typing import Optional

from Research.consistency_models import ConsistencyBreakdown
from Research.confidence_models import ConfidenceBreakdown
from Research.result import ResearchResult
from Research.robustness_models import RobustnessBreakdown
from Research.scoring import clamp, normalize_positive


class ConfidenceEngine:
    def evaluate(
        self,
        result: ResearchResult,
        robustness: RobustnessBreakdown,
        consistency: ConsistencyBreakdown,
    ) -> ConfidenceBreakdown:
        fold_count = len(result.walk_forward_folds)
        monthly_count = len(result.monthly_returns)
        yearly_count = len(result.yearly_returns)
        equity_points = len(result.equity_curve)

        data_coverage = mean(
            [
                normalize_positive(fold_count, 8.0),
                normalize_positive(monthly_count, 24.0),
                normalize_positive(yearly_count, 5.0),
                normalize_positive(equity_points, 36.0),
            ]
        )

        fold_quality = mean(
            [
                robustness.fold_success_score,
                robustness.degradation_score,
                robustness.fold_dispersion_score,
            ]
        )

        trade_sample = normalize_positive(
            result.metrics.total_trades,
            150.0,
        )

        regime_returns = result.diagnostics.get(
            "regime_returns",
            {},
        )

        regime_coverage = normalize_positive(
            len(regime_returns)
            if isinstance(regime_returns, dict)
            else 0,
            4.0,
        )

        stability_alignment = mean(
            [
                robustness.overall_robustness_score,
                consistency.overall_consistency_score,
            ]
        )

        oos_quality = mean(
            [
                robustness.degradation_score,
                consistency.fold_consistency_score,
                consistency.return_reliability_score,
            ]
        )

        overall = mean(
            [
                data_coverage,
                fold_quality,
                trade_sample,
                regime_coverage,
                stability_alignment,
                oos_quality,
            ]
        )

        return ConfidenceBreakdown(
            data_coverage_score=round(clamp(data_coverage), 4),
            fold_quality_score=round(clamp(fold_quality), 4),
            trade_sample_score=round(clamp(trade_sample), 4),
            regime_coverage_score=round(clamp(regime_coverage), 4),
            stability_alignment_score=round(
                clamp(stability_alignment),
                4,
            ),
            out_of_sample_quality_score=round(
                clamp(oos_quality),
                4,
            ),
            overall_confidence_score=round(
                clamp(overall),
                4,
            ),
        )
