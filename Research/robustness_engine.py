from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional

from Research.candidate import Candidate
from Research.result import ResearchResult
from Research.robustness_config import RobustnessWeights
from Research.robustness_models import RobustnessBreakdown
from Research.scoring import clamp


class RobustnessEngine:
    """
    Mengira robustness berdasarkan:
    - kejayaan fold out-of-sample
    - degradation train ke test
    - dispersion antara fold
    - kestabilan parameter
    - kestabilan regime
    """

    def __init__(
        self,
        weights: Optional[RobustnessWeights] = None,
    ) -> None:
        self.weights = weights or RobustnessWeights()

    def evaluate(
        self,
        candidate: Candidate,
        result: ResearchResult,
        peer_candidates: Optional[Iterable[Candidate]] = None,
    ) -> RobustnessBreakdown:
        folds = list(result.walk_forward_folds or [])

        fold_success_score = self._fold_success_score(folds)
        degradation_score = self._degradation_score(folds)
        fold_dispersion_score = self._fold_dispersion_score(folds)
        parameter_stability_score = self._parameter_stability_score(
            candidate,
            list(peer_candidates or []),
        )
        regime_stability_score = self._regime_stability_score(
            result.diagnostics
        )

        overall = (
            fold_success_score * self.weights.fold_success
            + degradation_score * self.weights.degradation
            + fold_dispersion_score * self.weights.fold_dispersion
            + parameter_stability_score * self.weights.parameter_stability
            + regime_stability_score * self.weights.regime_stability
        )

        return RobustnessBreakdown(
            fold_success_score=round(fold_success_score, 4),
            degradation_score=round(degradation_score, 4),
            fold_dispersion_score=round(fold_dispersion_score, 4),
            parameter_stability_score=round(parameter_stability_score, 4),
            regime_stability_score=round(regime_stability_score, 4),
            overall_robustness_score=round(clamp(overall), 4),
        )

    @staticmethod
    def _fold_success_score(
        folds: List[Dict[str, Any]],
    ) -> float:
        if not folds:
            return 0.0

        successful = 0

        for fold in folds:
            test_return = float(fold.get("test_return", 0.0))
            test_sharpe = float(fold.get("test_sharpe", 0.0))

            if test_return > 0 and test_sharpe > 0:
                successful += 1

        return clamp(successful / len(folds) * 100.0)

    @staticmethod
    def _degradation_score(
        folds: List[Dict[str, Any]],
    ) -> float:
        if not folds:
            return 0.0

        scores: List[float] = []

        for fold in folds:
            train_return = float(fold.get("train_return", 0.0))
            test_return = float(fold.get("test_return", 0.0))

            if train_return <= 0:
                scores.append(0.0)
                continue

            degradation = max(
                0.0,
                (train_return - test_return) / abs(train_return),
            )

            scores.append(
                clamp((1.0 - min(degradation, 1.0)) * 100.0)
            )

        return sum(scores) / len(scores)

    @staticmethod
    def _fold_dispersion_score(
        folds: List[Dict[str, Any]],
    ) -> float:
        if not folds:
            return 0.0

        returns = [
            float(fold.get("test_return", 0.0))
            for fold in folds
        ]

        if len(returns) == 1:
            return 100.0 if returns[0] > 0 else 0.0

        average = mean(returns)
        dispersion = pstdev(returns)

        denominator = max(abs(average), 1e-9)
        coefficient = dispersion / denominator

        return clamp((1.0 - min(coefficient, 1.0)) * 100.0)

    @staticmethod
    def _parameter_stability_score(
        candidate: Candidate,
        peers: List[Candidate],
    ) -> float:
        if not peers:
            return 70.0

        numeric_parameters = {
            key: float(value)
            for key, value in candidate.parameters.items()
            if isinstance(value, (int, float))
        }

        if not numeric_parameters:
            return 70.0

        distances: List[float] = []

        for peer in peers:
            if peer.candidate_id == candidate.candidate_id:
                continue

            if peer.strategy_name != candidate.strategy_name:
                continue

            shared = [
                key
                for key in numeric_parameters
                if key in peer.parameters
                and isinstance(peer.parameters[key], (int, float))
            ]

            if not shared:
                continue

            normalized_differences = []

            for key in shared:
                a = numeric_parameters[key]
                b = float(peer.parameters[key])
                scale = max(abs(a), abs(b), 1.0)
                normalized_differences.append(abs(a - b) / scale)

            distances.append(
                sum(normalized_differences) / len(normalized_differences)
            )

        if not distances:
            return 70.0

        nearest = min(distances)

        return clamp((1.0 - min(nearest, 1.0)) * 100.0)

    @staticmethod
    def _regime_stability_score(
        diagnostics: Dict[str, Any],
    ) -> float:
        if not diagnostics:
            return 50.0

        regime_returns = diagnostics.get("regime_returns")

        if not isinstance(regime_returns, dict) or not regime_returns:
            fold_count = int(diagnostics.get("fold_count", 0))
            return clamp(50.0 + min(fold_count, 10) * 5.0)

        values = [float(value) for value in regime_returns.values()]

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

        return clamp(
            positive_ratio * 70.0
            + dispersion_score * 0.30
        )
