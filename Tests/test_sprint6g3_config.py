"""
BursaAI v6 Sprint 6G.3 Unified Configuration Test.
"""

from pathlib import Path
import json
import os
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Config.config_loader import (
    load_app_config,
)


def main():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "config.json"

        path.write_text(
            json.dumps(
                {
                    "execution": {
                        "mode": "analysis",
                        "symbols": [
                            "1155.KL",
                            "1023.KL"
                        ],
                        "echo_logs": False
                    },
                    "paper_trading": {
                        "starting_capital": 150000
                    },
                    "notifications": {
                        "telegram_enabled": False
                    },
                    "walkforward": {
                        "symbol": "1155.KL",
                        "strategy_name": "ema_cross"
                    }
                }
            ),
            encoding="utf-8",
        )

        config = load_app_config(
            str(path)
        )

        assert config.execution.mode == "analysis"
        assert config.execution.symbols == [
            "1155.KL",
            "1023.KL"
        ]
        assert (
            config.paper_trading.starting_capital
            == 150000
        )
        assert (
            config.walkforward.strategy_name
            == "ema_cross"
        )

        os.environ[
            "BURSAAI_STARTING_CAPITAL"
        ] = "200000"

        os.environ[
            "BURSAAI_SYMBOLS"
        ] = "1295.KL,5819.KL"

        overridden = load_app_config(
            str(path)
        )

        assert (
            overridden.paper_trading.starting_capital
            == 200000
        )

        assert overridden.execution.symbols == [
            "1295.KL",
            "5819.KL"
        ]

        os.environ.pop(
            "BURSAAI_STARTING_CAPITAL",
            None,
        )

        os.environ.pop(
            "BURSAAI_SYMBOLS",
            None,
        )

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.3 CONFIG TEST")
    print("=" * 92)
    print("JSON Config Load         : OK")
    print("Nested Config Models     : OK")
    print("Config Validation        : OK")
    print("Environment Override     : OK")
    print("Symbol Parsing           : OK")
    print("Capital Override         : OK")
    print("=" * 92)
    print("SPRINT 6G.3 UNIFIED CONFIGURATION OK")


if __name__ == "__main__":
    main()
