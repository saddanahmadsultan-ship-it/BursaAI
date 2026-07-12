"""
=========================================================
BursaAI Configuration Loader
Version : 6.0 Sprint 6G.3
=========================================================
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from Config.app_config import (
    AppConfig,
    ExecutionConfig,
    FeatureConfig,
    NotificationConfig,
    PaperTradingConfig,
    WalkForwardConfig,
)


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def _read_json(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    return json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )


def load_app_config(
    path: str | None = None,
) -> AppConfig:
    raw = _read_json(path)

    raw_features = dict(
        raw.get("features", {})
    )

    raw_execution = dict(
        raw.get("execution", {})
    )

    raw_paper = dict(
        raw.get("paper_trading", {})
    )

    raw_notifications = dict(
        raw.get("notifications", {})
    )

    raw_walkforward = dict(
        raw.get("walkforward", {})
    )

    features = FeatureConfig(
        enable_analysis=_bool(
            os.getenv(
                "BURSAAI_ENABLE_ANALYSIS",
                raw_features.get(
                    "enable_analysis",
                    True,
                ),
            ),
            True,
        ),
        enable_portfolio=_bool(
            os.getenv(
                "BURSAAI_ENABLE_PORTFOLIO",
                raw_features.get(
                    "enable_portfolio",
                    True,
                ),
            ),
            True,
        ),
        enable_paper_trading=_bool(
            os.getenv(
                "BURSAAI_ENABLE_PAPER_TRADING",
                raw_features.get(
                    "enable_paper_trading",
                    True,
                ),
            ),
            True,
        ),
        enable_notifications=_bool(
            os.getenv(
                "BURSAAI_ENABLE_NOTIFICATIONS",
                raw_features.get(
                    "enable_notifications",
                    True,
                ),
            ),
            True,
        ),
        enable_journal=_bool(
            os.getenv(
                "BURSAAI_ENABLE_JOURNAL",
                raw_features.get(
                    "enable_journal",
                    True,
                ),
            ),
            True,
        ),
        enable_analytics=_bool(
            os.getenv(
                "BURSAAI_ENABLE_ANALYTICS",
                raw_features.get(
                    "enable_analytics",
                    True,
                ),
            ),
            True,
        ),
        enable_walkforward=_bool(
            os.getenv(
                "BURSAAI_ENABLE_WALKFORWARD",
                raw_features.get(
                    "enable_walkforward",
                    False,
                ),
            ),
            False,
        ),
    )

    execution = ExecutionConfig(
        mode=str(
            os.getenv(
                "BURSAAI_MODE",
                raw_execution.get(
                    "mode",
                    "analysis",
                ),
            )
        ),
        failure_mode=str(
            os.getenv(
                "BURSAAI_FAILURE_MODE",
                raw_execution.get(
                    "failure_mode",
                    "stop",
                ),
            )
        ),
        echo_logs=_bool(
            os.getenv(
                "BURSAAI_ECHO_LOGS",
                raw_execution.get(
                    "echo_logs",
                    True,
                ),
            ),
            True,
        ),
        symbols=_list(
            os.getenv(
                "BURSAAI_SYMBOLS",
                raw_execution.get(
                    "symbols",
                    [],
                ),
            )
        ),
        pipeline_version=str(
            raw_execution.get(
                "pipeline_version",
                "6.0",
            )
        ),
    )

    paper = PaperTradingConfig(
        starting_capital=_float(
            os.getenv(
                "BURSAAI_STARTING_CAPITAL",
                raw_paper.get(
                    "starting_capital",
                    100000,
                ),
            ),
            100000,
        ),
        slippage_percent=_float(
            os.getenv(
                "BURSAAI_SLIPPAGE_PERCENT",
                raw_paper.get(
                    "slippage_percent",
                    0,
                ),
            ),
            0,
        ),
        commission_flat=_float(
            os.getenv(
                "BURSAAI_COMMISSION_FLAT",
                raw_paper.get(
                    "commission_flat",
                    0,
                ),
            ),
            0,
        ),
    )

    notifications = NotificationConfig(
        telegram_enabled=_bool(
            os.getenv(
                "BURSAAI_TELEGRAM_ENABLED",
                raw_notifications.get(
                    "telegram_enabled",
                    False,
                ),
            ),
            False,
        ),
        telegram_dry_run=_bool(
            os.getenv(
                "BURSAAI_TELEGRAM_DRY_RUN",
                raw_notifications.get(
                    "telegram_dry_run",
                    True,
                ),
            ),
            True,
        ),
    )

    walkforward = WalkForwardConfig(
        symbol=str(
            os.getenv(
                "BURSAAI_WF_SYMBOL",
                raw_walkforward.get(
                    "symbol",
                    "",
                ),
            )
        ),
        strategy_name=str(
            os.getenv(
                "BURSAAI_WF_STRATEGY",
                raw_walkforward.get(
                    "strategy_name",
                    "default",
                ),
            )
        ),
        optimization_mode=str(
            os.getenv(
                "BURSAAI_WF_OPTIMIZATION_MODE",
                raw_walkforward.get(
                    "optimization_mode",
                    "grid",
                ),
            )
        ),
        random_count=_int(
            os.getenv(
                "BURSAAI_WF_RANDOM_COUNT",
                raw_walkforward.get(
                    "random_count",
                    10,
                ),
            ),
            10,
        ),
        export_report=_bool(
            os.getenv(
                "BURSAAI_WF_EXPORT_REPORT",
                raw_walkforward.get(
                    "export_report",
                    True,
                ),
            ),
            True,
        ),
        output_directory=str(
            os.getenv(
                "BURSAAI_WF_OUTPUT_DIRECTORY",
                raw_walkforward.get(
                    "output_directory",
                    "Reports/WalkForward",
                ),
            )
        ),
    )

    config = AppConfig(
        app_name=str(
            raw.get(
                "app_name",
                "BursaAI",
            )
        ),
        version=str(
            raw.get(
                "version",
                "6.0",
            )
        ),
        environment=str(
            os.getenv(
                "BURSAAI_ENVIRONMENT",
                raw.get(
                    "environment",
                    "development",
                ),
            )
        ),
        features=features,
        execution=execution,
        paper_trading=paper,
        notifications=notifications,
        walkforward=walkforward,
        journal_database_path=str(
            os.getenv(
                "BURSAAI_JOURNAL_DATABASE",
                raw.get(
                    "journal_database_path",
                    "Data/bursaai_journal.db",
                ),
            )
        ),
        metadata=dict(
            raw.get("metadata", {})
        ),
    )

    config.validate()

    return config
