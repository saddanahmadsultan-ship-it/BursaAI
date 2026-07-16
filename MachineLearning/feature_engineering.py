from __future__ import annotations

import math
from typing import Any, Dict


class ResearchFeatureEngineer:
    BASE_FEATURES = (
        "overall_score",
        "performance_score",
        "risk_score",
        "consistency_score",
        "robustness_score",
        "confidence_score",
        "cagr",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "volatility",
        "profit_factor",
        "recovery_factor",
        "win_rate",
        "total_trades",
        "pareto_front",
        "crowding_distance",
    )

    ENGINEERED_FEATURES = (
        "risk_adjusted_performance",
        "stability_composite",
        "quality_composite",
        "confidence_stability",
        "return_drawdown_ratio",
        "trade_sample_log",
        "pareto_quality",
        "score_confidence_interaction",
        "robustness_consistency_gap",
        "downside_pressure",
    )

    def transform(
        self,
        raw: Dict[str, Any],
    ) -> Dict[str, float]:
        values = {
            name: self._finite_float(
                raw.get(name, 0.0)
            )
            for name in self.BASE_FEATURES
        }

        overall = values["overall_score"]
        performance = values["performance_score"]
        risk = values["risk_score"]
        consistency = values["consistency_score"]
        robustness = values["robustness_score"]
        confidence = values["confidence_score"]
        cagr = values["cagr"]
        drawdown = abs(values["max_drawdown"])
        volatility = abs(values["volatility"])
        total_trades = max(values["total_trades"], 0.0)
        pareto_front = max(values["pareto_front"], 1.0)
        crowding = max(values["crowding_distance"], 0.0)

        values.update(
            {
                "risk_adjusted_performance": self._safe_div(
                    performance * risk,
                    100.0,
                ),
                "stability_composite": (
                    robustness + consistency
                ) / 2.0,
                "quality_composite": (
                    overall * 0.35
                    + robustness * 0.20
                    + consistency * 0.20
                    + confidence * 0.15
                    + risk * 0.10
                ),
                "confidence_stability": self._safe_div(
                    confidence
                    * ((robustness + consistency) / 2.0),
                    100.0,
                ),
                "return_drawdown_ratio": self._safe_div(
                    cagr,
                    max(drawdown, 0.01),
                ),
                "trade_sample_log": math.log1p(
                    total_trades
                ),
                "pareto_quality": self._safe_div(
                    100.0 + min(crowding, 10.0) * 5.0,
                    pareto_front,
                ),
                "score_confidence_interaction": self._safe_div(
                    overall * confidence,
                    100.0,
                ),
                "robustness_consistency_gap": abs(
                    robustness - consistency
                ),
                "downside_pressure": (
                    drawdown + volatility
                ) / 2.0,
            }
        )

        return {
            key: round(self._finite_float(value), 8)
            for key, value in values.items()
        }

    @staticmethod
    def _safe_div(
        numerator: float,
        denominator: float,
    ) -> float:
        if abs(denominator) < 1e-12:
            return 0.0
        return numerator / denominator

    @staticmethod
    def _finite_float(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not math.isfinite(number):
            return 0.0

        return number
