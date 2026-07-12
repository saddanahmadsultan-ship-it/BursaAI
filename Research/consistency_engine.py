from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List, Optional

from Research.consistency_config import ConsistencyWeights
from Research.consistency_models import ConsistencyBreakdown
from Research.result import ResearchResult
from Research.scoring import clamp


class ConsistencyEngine:
    """
    Mengira consistency berdasarkan:
    - kestabilan hasil antara walk-forward fold
    - kestabilan pulangan bulanan
    - kestabilan pulangan tahunan
    - kelicinan equity curve
    - kebolehpercayaan pulangan positif
    """

    def __init__(
        self,
        weights: Optional[ConsistencyWeights] = None,
    ) -> None:
        self.weights = weights or ConsistencyWeights()

    def evaluate(
        self,
        result: ResearchResult,
    ) -> ConsistencyBreakdown:
        fold_consistency = self._fold_consistency_score(
            list(result.walk_forward_folds or [])
        )

        monthly_stability = self._period_stability_score(
            result.monthly_returns
        )

        yearly_stability = self._period_stability_score(
            result.yearly_returns
        )

        equity_smoothness = self._equity_smoothness_score(
            list(result.equity_curve or [])
        )

        return_reliability = self._return_reliability_score(
            result
        )

        overall = (
            fold_consistency * self.weights.fold_consistency
            + monthly_stability * self.weights.monthly_stability
            + yearly_stability * self.weights.yearly_stability
            + equity_smoothness * self.weights.equity_smoothness
            + return_reliability * self.weights.return_reliability
        )

        return ConsistencyBreakdown(
            fold_consistency_score=round(fold_consistency, 4),
            monthly_stability_score=round(monthly_stability, 4),
            yearly_stability_score=round(yearly_stability, 4),
            equity_smoothness_score=round(equity_smoothness, 4),
            return_reliability_score=round(return_reliability, 4),
            overall_consistency_score=round(clamp(overall), 4),
        )

    @staticmethod
    def _fold_consistency_score(
        folds: List[Dict[str, Any]],
    ) -> float:
        if not folds:
            return 0.0

        values = [
            float(fold.get("test_return", 0.0))
            for fold in folds
        ]

        if len(values) == 1:
            return 100.0 if values[0] > 0 else 0.0

        average = mean(values)
        dispersion = pstdev(values)
        denominator = max(abs(average), 1e-9)
        coefficient = dispersion / denominator

        positive_ratio = (
            sum(value > 0 for value in values)
            / len(values)
        )

        dispersion_score = clamp(
            (1.0 - min(coefficient, 1.0)) * 100.0
        )

        return clamp(
            dispersion_score * 0.70
            + positive_ratio * 100.0 * 0.30
        )

    @staticmethod
    def _period_stability_score(
        values_map: Dict[str, float],
    ) -> float:
        if not isinstance(values_map, dict) or not values_map:
            return 0.0

        values = [
            float(value)
            for value in values_map.values()
        ]

        positive_ratio = (
            sum(value > 0 for value in values)
            / len(values)
        )

        if len(values) == 1:
            dispersion_score = 100.0
        else:
            average = mean(values)
            dispersion = pstdev(values)
            coefficient = dispersion / max(abs(average), 1e-9)

            dispersion_score = clamp(
                (1.0 - min(coefficient, 1.0)) * 100.0
            )

        downside_penalty = (
            sum(abs(value) for value in values if value < 0)
            / max(
                sum(abs(value) for value in values),
                1e-9,
            )
        )

        return clamp(
            positive_ratio * 50.0
            + dispersion_score * 0.40
            + (1.0 - downside_penalty) * 10.0
        )

    @staticmethod
    def _equity_smoothness_score(
        equity_curve: List[Dict[str, Any]],
    ) -> float:
        if len(equity_curve) < 2:
            return 0.0

        equity_values = [
            float(point.get("equity", 0.0))
            for point in equity_curve
        ]

        if any(value <= 0 for value in equity_values):
            return 0.0

        returns = []

        for previous, current in zip(
            equity_values,
            equity_values[1:],
        ):
            returns.append(
                (current / previous) - 1.0
            )

        positive_ratio = (
            sum(value >= 0 for value in returns)
            / len(returns)
        )

        if len(returns) == 1:
            volatility_score = 100.0
        else:
            average = mean(returns)
            dispersion = pstdev(returns)
            coefficient = dispersion / max(abs(average), 1e-9)

            volatility_score = clamp(
                (1.0 - min(coefficient, 1.0)) * 100.0
            )

        max_step_drawdown = min(returns)
        drawdown_score = clamp(
            (1.0 - min(abs(min(max_step_drawdown, 0.0)), 0.20) / 0.20)
            * 100.0
        )

        return clamp(
            positive_ratio * 40.0
            + volatility_score * 0.40
            + drawdown_score * 0.20
        )

    @staticmethod
    def _return_reliability_score(
        result: ResearchResult,
    ) -> float:
        sources = []

        fold_values = [
            float(fold.get("test_return", 0.0))
            for fold in result.walk_forward_folds
        ]

        monthly_values = [
            float(value)
            for value in result.monthly_returns.values()
        ]

        yearly_values = [
            float(value)
            for value in result.yearly_returns.values()
        ]

        if fold_values:
            sources.append(
                sum(value > 0 for value in fold_values)
                / len(fold_values)
            )

        if monthly_values:
            sources.append(
                sum(value > 0 for value in monthly_values)
                / len(monthly_values)
            )

        if yearly_values:
            sources.append(
                sum(value > 0 for value in yearly_values)
                / len(yearly_values)
            )

        if not sources:
            return 0.0

        win_rate_component = clamp(
            result.metrics.win_rate
        ) / 100.0

        return clamp(
            mean(sources) * 80.0
            + win_rate_component * 20.0
        )
