from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from Research.candidate import Candidate
from Research.metrics import PerformanceMetrics
from Research.result import ResearchResult


WalkForwardCallable = Callable[
    [Candidate],
    Dict[str, Any],
]


@dataclass
class WalkForwardAdapterConfig:
    minimum_folds: int = 1
    require_equity_curve: bool = False

    def __post_init__(self) -> None:
        self.minimum_folds = max(
            1,
            int(self.minimum_folds),
        )


class WalkForwardAdapter:
    """
    Adapter neutral antara Research Engine dan Walk Forward Engine.

    walk_forward_callable(candidate) mesti memulangkan dictionary:

    {
        "metrics": {...},
        "folds": [...],
        "monthly_returns": {...},
        "yearly_returns": {...},
        "equity_curve": [...],
        "trade_summary": {...},
        "diagnostics": {...}
    }
    """

    def __init__(
        self,
        walk_forward_callable: WalkForwardCallable,
        config: Optional[
            WalkForwardAdapterConfig
        ] = None,
    ) -> None:
        if not callable(walk_forward_callable):
            raise TypeError(
                "walk_forward_callable mesti callable."
            )

        self.walk_forward_callable = (
            walk_forward_callable
        )
        self.config = (
            config or WalkForwardAdapterConfig()
        )

    def evaluate(
        self,
        experiment_id: str,
        candidate: Candidate,
    ) -> ResearchResult:
        started = time.monotonic()

        try:
            raw = self.walk_forward_callable(candidate)

            if not isinstance(raw, dict):
                raise TypeError(
                    "Walk Forward Engine mesti "
                    "memulangkan dictionary."
                )

            metrics = PerformanceMetrics.from_dict(
                raw.get("metrics")
            )

            folds = raw.get("folds", [])

            if len(folds) < self.config.minimum_folds:
                raise ValueError(
                    "Bilangan walk-forward fold tidak mencukupi."
                )

            equity_curve = raw.get(
                "equity_curve",
                [],
            )

            if (
                self.config.require_equity_curve
                and not equity_curve
            ):
                raise ValueError(
                    "Equity curve diperlukan tetapi kosong."
                )

            return ResearchResult(
                experiment_id=experiment_id,
                candidate_id=candidate.candidate_id,
                candidate_hash=candidate.candidate_hash,
                metrics=metrics,
                walk_forward_folds=folds,
                monthly_returns=raw.get(
                    "monthly_returns",
                    {},
                ),
                yearly_returns=raw.get(
                    "yearly_returns",
                    {},
                ),
                equity_curve=equity_curve,
                trade_summary=raw.get(
                    "trade_summary",
                    {},
                ),
                diagnostics=raw.get(
                    "diagnostics",
                    {},
                ),
                execution_seconds=(
                    time.monotonic() - started
                ),
            )

        except Exception as exc:
            return ResearchResult(
                experiment_id=experiment_id,
                candidate_id=candidate.candidate_id,
                candidate_hash=candidate.candidate_hash,
                metrics=PerformanceMetrics(),
                execution_seconds=(
                    time.monotonic() - started
                ),
                diagnostics={
                    "adapter_error_type": (
                        type(exc).__name__
                    )
                },
                error_message=str(exc),
            )

    def evaluator(
        self,
        experiment_id: str,
        result_callback: Optional[
            Callable[[ResearchResult], None]
        ] = None,
    ) -> Callable[[Candidate], PerformanceMetrics]:
        """
        Menghasilkan evaluator yang serasi dengan ExperimentRunner.
        """

        def _evaluate(
            candidate: Candidate,
        ) -> PerformanceMetrics:
            result = self.evaluate(
                experiment_id,
                candidate,
            )

            if result_callback is not None:
                result_callback(result)

            if not result.successful:
                raise RuntimeError(
                    result.error_message
                    or "Walk Forward evaluation gagal."
                )

            return result.metrics

        return _evaluate
