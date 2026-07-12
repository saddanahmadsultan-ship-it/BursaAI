"""
=========================================================
BursaAI Unified Application Configuration
Version : 6.0 Sprint 6G.3
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class FeatureConfig:
    enable_analysis: bool = True
    enable_portfolio: bool = True
    enable_paper_trading: bool = True
    enable_notifications: bool = True
    enable_journal: bool = True
    enable_analytics: bool = True
    enable_walkforward: bool = False


@dataclass(slots=True)
class ExecutionConfig:
    mode: str = "analysis"
    failure_mode: str = "stop"
    echo_logs: bool = True
    symbols: List[str] = field(default_factory=list)
    pipeline_version: str = "6.0"


@dataclass(slots=True)
class PaperTradingConfig:
    starting_capital: float = 100000.0
    slippage_percent: float = 0.0
    commission_flat: float = 0.0


@dataclass(slots=True)
class NotificationConfig:
    telegram_enabled: bool = False
    telegram_dry_run: bool = True


@dataclass(slots=True)
class WalkForwardConfig:
    symbol: str = ""
    strategy_name: str = "default"
    optimization_mode: str = "grid"
    random_count: int = 10
    export_report: bool = True
    output_directory: str = "Reports/WalkForward"


@dataclass(slots=True)
class AppConfig:
    app_name: str = "BursaAI"
    version: str = "6.0"
    environment: str = "development"

    features: FeatureConfig = field(
        default_factory=FeatureConfig
    )
    execution: ExecutionConfig = field(
        default_factory=ExecutionConfig
    )
    paper_trading: PaperTradingConfig = field(
        default_factory=PaperTradingConfig
    )
    notifications: NotificationConfig = field(
        default_factory=NotificationConfig
    )
    walkforward: WalkForwardConfig = field(
        default_factory=WalkForwardConfig
    )

    journal_database_path: str = (
        "Data/bursaai_journal.db"
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        valid_modes = {
            "analysis",
            "paper",
            "walkforward",
            "health",
        }

        mode = self.execution.mode.lower()

        if mode not in valid_modes:
            raise ValueError(
                f"Invalid execution mode: {self.execution.mode}"
            )

        if self.paper_trading.starting_capital <= 0:
            raise ValueError(
                "Starting capital must be greater than zero."
            )

        if self.paper_trading.slippage_percent < 0:
            raise ValueError(
                "Slippage percent cannot be negative."
            )

        if self.paper_trading.commission_flat < 0:
            raise ValueError(
                "Commission cannot be negative."
            )

        if (
            mode == "walkforward"
            and not self.walkforward.symbol.strip()
        ):
            raise ValueError(
                "Walk Forward mode requires a symbol."
            )

        if (
            mode == "analysis"
            and not self.execution.symbols
        ):
            raise ValueError(
                "Analysis mode requires at least one symbol."
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
