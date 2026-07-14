from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from Research import (
    AIRankingEngine,
    Experiment,
    ExperimentMode,
    ExperimentRegistry,
    ExperimentRunner,
    LeaderboardExporter,
    ParameterSpace,
    ParetoEngine,
    ParetoReportExporter,
    PromotionEngine,
    ResearchResultStore,
    RunnerConfig,
    WalkForwardAdapter,
)


@dataclass
class UnifiedPipelineConfig:
    project_root: Path
    experiment_name: str = "BursaAI Sprint 7A.5 Final RC"
    symbol: str = "1155.KL"
    max_candidates: int = 12
    max_workers: int = 4
    checkpoint_every: int = 2
    max_retries: int = 1


class UnifiedResearchPipeline:
    def __init__(
        self,
        walk_forward_callable,
        config: UnifiedPipelineConfig,
    ) -> None:
        self.walk_forward_callable = walk_forward_callable
        self.config = config

    def run(self) -> Dict[str, Any]:
        root = self.config.project_root

        registry = ExperimentRegistry(
            root / "Experiments"
        )

        result_store = ResearchResultStore(
            root / "ResearchResults"
        )

        parameter_space = ParameterSpace(
            strategy_name="EMA_RSI_ATR",
            parameters={
                "ema_fast": [10, 20, 30],
                "ema_slow": [50, 100],
                "rsi_period": [8, 10, 14],
                "atr_multiplier": [1.5, 2.0],
            },
        )

        experiment = Experiment(
            name=self.config.experiment_name,
            description=(
                "Unified Research Pipeline integrating "
                "Walk Forward, Ranking, Robustness, "
                "Consistency, Confidence, Pareto and Tier Gate."
            ),
            mode=ExperimentMode.PARALLEL,
            candidates=parameter_space.generate_grid_candidates(
                symbol=self.config.symbol,
                max_candidates=self.config.max_candidates,
            ),
            symbols=[self.config.symbol],
        )

        registry.register(experiment)

        adapter = WalkForwardAdapter(
            self.walk_forward_callable
        )

        runner = ExperimentRunner(
            registry=registry,
            evaluator=adapter.evaluator(
                experiment.experiment_id,
                result_callback=result_store.save,
            ),
            config=RunnerConfig(
                max_workers=self.config.max_workers,
                checkpoint_every=self.config.checkpoint_every,
                max_retries=self.config.max_retries,
            ),
        )

        runner_stats = runner.run(experiment)
        restored = registry.load(experiment.experiment_id)

        entries = result_store.list(
            experiment_id=restored.experiment_id
        )

        by_candidate = {
            item["candidate_id"]: item
            for item in entries
        }

        pairs = []

        for candidate in restored.candidates:
            entry = by_candidate.get(candidate.candidate_id)
            if entry is None:
                continue

            result = result_store.load(entry["result_id"])
            pairs.append((candidate, result))

        leaderboard = AIRankingEngine().rank(pairs)
        pareto_points = ParetoEngine().rank(leaderboard)
        promotions = PromotionEngine().evaluate(
            leaderboard,
            pareto_points,
        )

        ranking_outputs = LeaderboardExporter(
            root / "Reports" / "Ranking"
        ).export_all(leaderboard)

        pareto_outputs = ParetoReportExporter(
            root / "Reports" / "Pareto"
        ).export(
            pareto_points,
            promotions,
        )

        top = leaderboard[0] if leaderboard else None

        return {
            "experiment_id": restored.experiment_id,
            "status": restored.status.value,
            "total_candidates": restored.total_candidates,
            "completed_candidates": restored.completed_candidates,
            "failed_candidates": restored.failed_candidates,
            "runner_stats": runner_stats.to_dict(),
            "leaderboard": leaderboard,
            "pareto_points": pareto_points,
            "promotions": promotions,
            "ranking_outputs": ranking_outputs,
            "pareto_outputs": pareto_outputs,
            "top_candidate": top,
        }
