"""
=========================================================
BursaAI v6 Unified Entry Point
Version : 6.0 Sprint 6G.3
=========================================================

Usage:
    python main_v6.py
    python main_v6.py --config Config/default_config.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from Bootstrap.application_runner import (
    ApplicationRunner,
)
from Bootstrap.service_bootstrap import (
    BootstrapOptions,
    UnifiedServiceBootstrap,
)
from Config.config_loader import (
    load_app_config,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="BursaAI v6 Unified Runner"
    )

    parser.add_argument(
        "--config",
        default="Config/default_config.json",
        help="Path to JSON configuration file.",
    )

    parser.add_argument(
        "--output",
        default="",
        help="Optional JSON result output path.",
    )

    return parser.parse_args()


def build_application(config):
    options = BootstrapOptions(
        enable_paper_trading=(
            config.features.enable_paper_trading
        ),
        enable_notifications=(
            config.features.enable_notifications
        ),
        enable_journal=(
            config.features.enable_journal
        ),
        enable_analytics=(
            config.features.enable_analytics
        ),
        enable_walkforward=(
            config.features.enable_walkforward
        ),
        starting_capital=(
            config.paper_trading.starting_capital
        ),
        journal_database_path=(
            config.journal_database_path
        ),
        telegram_enabled=(
            config.notifications.telegram_enabled
        ),
        telegram_dry_run=(
            config.notifications.telegram_dry_run
        ),
        pipeline_failure_mode=(
            config.execution.failure_mode
        ),
        echo_logs=(
            config.execution.echo_logs
        ),
    )

    return UnifiedServiceBootstrap(
        options
    ).build()


def main():
    args = parse_args()
    config = load_app_config(
        args.config
    )

    application = build_application(
        config
    )

    result = ApplicationRunner(
        application=application,
        config=config,
    ).run()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    if args.output:
        path = Path(args.output)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
