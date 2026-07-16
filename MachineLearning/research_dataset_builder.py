from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping

from MachineLearning.dataset import MLDataset
from MachineLearning.feature_engineering import (
    ResearchFeatureEngineer,
)
from MachineLearning.feature_schema import FeatureSchema
from MachineLearning.label_builder import (
    ResearchLabelBuilder,
)


class ResearchDatasetBuilder:
    def __init__(
        self,
        feature_engineer: ResearchFeatureEngineer | None = None,
        label_builder: ResearchLabelBuilder | None = None,
    ) -> None:
        self.feature_engineer = (
            feature_engineer
            or ResearchFeatureEngineer()
        )
        self.label_builder = (
            label_builder
            or ResearchLabelBuilder()
        )

    def build(
        self,
        ranked_strategies: Iterable[Any],
        pareto_points: Iterable[Any] | None = None,
        promotions: Iterable[Mapping[str, Any]] | None = None,
        scale: bool = False,
    ) -> MLDataset:
        pareto_map = self._pareto_map(
            pareto_points or []
        )

        promotion_map = {
            str(item.get("candidate_id")): dict(item)
            for item in (promotions or [])
        }

        records: List[Dict[str, Any]] = []

        for strategy in ranked_strategies:
            item = self._to_dict(strategy)
            candidate_id = str(
                item.get("candidate_id", "")
            )

            raw = self._flatten_strategy(
                item,
                pareto_map.get(candidate_id, {}),
                promotion_map.get(candidate_id, {}),
            )

            engineered = self.feature_engineer.transform(
                raw
            )

            engineered["promoted"] = (
                self.label_builder.build(raw)
            )

            engineered["metadata"] = {
                "candidate_id": candidate_id,
                "candidate_name": item.get(
                    "candidate_name",
                    "",
                ),
                "experiment_id": item.get(
                    "experiment_id",
                    "",
                ),
                "strategy_name": item.get(
                    "strategy_name",
                    "",
                ),
                "tier": raw.get("tier", ""),
                "promotion_action": raw.get(
                    "promotion_action",
                    "",
                ),
            }

            records.append(engineered)

        feature_names = list(
            ResearchFeatureEngineer.BASE_FEATURES
            + ResearchFeatureEngineer.ENGINEERED_FEATURES
        )

        schema = FeatureSchema.from_names(
            feature_names,
            target_name="promoted",
        )

        dataset = MLDataset.from_records(
            schema,
            records,
        )

        if scale:
            from MachineLearning.feature_scaler import (
                StandardFeatureScaler,
            )

            scaler = StandardFeatureScaler()
            scaler.fit(dataset.rows)
            dataset.rows = scaler.transform(
                dataset.rows
            )

        return dataset

    @staticmethod
    def _to_dict(item: Any) -> Dict[str, Any]:
        if isinstance(item, dict):
            return dict(item)

        if hasattr(item, "to_dict"):
            return dict(item.to_dict())

        raise TypeError(
            "Ranked strategy mesti dict atau mempunyai to_dict()."
        )

    @staticmethod
    def _pareto_map(
        points: Iterable[Any],
    ) -> Dict[str, Dict[str, Any]]:
        result = {}

        for point in points:
            if isinstance(point, dict):
                payload = dict(point)
            elif hasattr(point, "to_dict"):
                payload = dict(point.to_dict())
            else:
                continue

            result[
                str(payload.get("candidate_id", ""))
            ] = payload

        return result

    @staticmethod
    def _flatten_strategy(
        strategy: Dict[str, Any],
        pareto: Dict[str, Any],
        promotion: Dict[str, Any],
    ) -> Dict[str, Any]:
        breakdown = strategy.get(
            "breakdown",
            {},
        ) or {}

        metrics = strategy.get(
            "metrics",
            {},
        ) or {}

        return {
            "overall_score": breakdown.get(
                "overall_score",
                0.0,
            ),
            "performance_score": breakdown.get(
                "performance_score",
                0.0,
            ),
            "risk_score": breakdown.get(
                "risk_score",
                metrics.get("risk_score", 0.0),
            ),
            "consistency_score": breakdown.get(
                "consistency_score",
                0.0,
            ),
            "robustness_score": breakdown.get(
                "robustness_score",
                0.0,
            ),
            "confidence_score": breakdown.get(
                "confidence_score",
                0.0,
            ),
            "cagr": metrics.get("cagr", 0.0),
            "sharpe_ratio": metrics.get(
                "sharpe_ratio",
                0.0,
            ),
            "sortino_ratio": metrics.get(
                "sortino_ratio",
                0.0,
            ),
            "max_drawdown": metrics.get(
                "max_drawdown",
                0.0,
            ),
            "volatility": metrics.get(
                "volatility",
                0.0,
            ),
            "profit_factor": metrics.get(
                "profit_factor",
                0.0,
            ),
            "recovery_factor": metrics.get(
                "recovery_factor",
                0.0,
            ),
            "win_rate": metrics.get(
                "win_rate",
                0.0,
            ),
            "total_trades": metrics.get(
                "total_trades",
                0.0,
            ),
            "pareto_front": pareto.get(
                "front",
                promotion.get(
                    "pareto_front",
                    99,
                ),
            ),
            "crowding_distance": ResearchDatasetBuilder._finite(
                pareto.get(
                    "crowding_distance",
                    0.0,
                )
            ),
            "tier": strategy.get(
                "tier",
                "",
            ),
            "approved_tier": promotion.get(
                "approved_tier",
                strategy.get("tier", ""),
            ),
            "promotion_action": promotion.get(
                "action",
                strategy.get(
                    "recommendation",
                    "",
                ),
            ),
        }

    @staticmethod
    def _finite(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        return number if math.isfinite(number) else 0.0
