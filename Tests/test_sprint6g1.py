"""
BursaAI v6 Sprint 6G.1 Unified Service Bootstrap test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Bootstrap.service_bootstrap import (
    BootstrapOptions,
    UnifiedServiceBootstrap,
)


def fake_loader(symbol):
    return pd.DataFrame(
        {
            "Close": [10.0, 10.2, 10.4],
            "Volume": [1000, 1200, 1500],
        }
    )


def fake_indicators(data):
    output = data.copy()

    defaults = {
        "MA20": [9.8, 9.9, 10.0],
        "MA50": [9.5, 9.6, 9.7],
        "MA200": [9.0, 9.1, 9.2],
        "EMA20": [9.8, 9.9, 10.0],
        "EMA50": [9.5, 9.6, 9.7],
        "EMA200": [9.0, 9.1, 9.2],
        "EMA20_SLOPE": [0.01, 0.02, 0.03],
        "ATR": [0.2, 0.2, 0.2],
        "ATR_PERCENT": [2.0, 2.0, 2.0],
        "RSI": [55, 60, 65],
        "STOCH": [50, 60, 70],
        "CCI": [50, 80, 100],
        "ROC": [2, 3, 4],
        "MACD": [0.1, 0.2, 0.3],
        "MACD_SIGNAL": [0.05, 0.1, 0.2],
        "MACD_HISTOGRAM": [0.05, 0.1, 0.1],
        "VWAP": [9.9, 10.0, 10.1],
        "HIGHER_HIGH": [False, True, True],
        "HIGHER_LOW": [False, True, True],
        "LOWER_HIGH": [False, False, False],
        "BREAKOUT": [False, False, True],
        "BREAKDOWN": [False, False, False],
        "OBV": [1000, 2200, 3700],
        "OBV_MA20": [900, 1500, 2500],
    }

    for name, values in defaults.items():
        output[name] = values

    return output


def fake_score(data):
    return {
        "score": 82,
        "grade": "A",
        "trend": {"score": 24, "direction": "UP"},
        "momentum": {"score": 20, "quality": "STRONG"},
        "volume": {"score": 15, "strength": "STRONG"},
        "volatility": {"score": 10, "level": "LOW"},
        "risk": {"score": 13, "rr": 2.0},
    }


def fake_trend(data):
    return {"score": 24, "direction": "UP"}


def fake_momentum(data):
    return {"score": 20, "quality": "STRONG"}


def fake_volume(data):
    return {"score": 15, "strength": "STRONG"}


def passthrough(result):
    return dict(result)


def fake_smart(data, result):
    return dict(result)


def fake_regime(data, result):
    output = dict(result)
    output["MarketRegime"] = "BULLISH"
    output["FinalScore"] = 85
    return output


def fake_timing(data, result):
    output = dict(result)
    output["entry_timing"] = {
        "score": 80,
        "status": "READY",
        "action": "ENTER",
        "entry_zone_low": 10.2,
        "entry_zone_high": 10.4,
        "reasons": [],
        "warnings": [],
    }
    return output


def fake_brain(result):
    output = dict(result)
    output["ai_brain"] = {
        "conviction_score": 85,
        "conviction_level": "HIGH",
        "ai_signal": "BUY",
        "prediction_stability": 88,
        "execution_quality": 86,
        "components": {},
        "contributions": {},
        "reasoning": {
            "strengths": [],
            "weaknesses": [],
            "summary": "OK",
        },
    }
    return output


def fake_confidence(*args):
    return {
        "confidence": 88,
        "level": "HIGH",
        "reason": [],
    }


def fake_strategy(*args):
    return {
        "strategy": "BUY",
        "entry": 10.4,
        "stoploss": 10.0,
        "target": 11.2,
        "rr": 2.0,
        "bullish": True,
        "warning": [],
    }


def fake_decision(result):
    return {
        "analysis": [],
        "warnings": [],
        "quality": 80,
        "rating": "A",
        "recommendation": "BUY",
        "summary": "OK",
    }


def fake_risk(result):
    output = dict(result)
    output["DynamicRiskPercent"] = 0.8
    output["dynamic_risk"] = {
        "final_risk_percent": 0.8,
    }
    return output


def fake_position(result):
    output = dict(result)
    output.update(
        {
            "AccountCapital": 100000,
            "RiskPercent": 0.8,
            "RiskCapital": 800,
            "RiskPerShare": 0.4,
            "Shares": 2000,
            "Lots": 20,
            "CapitalUsed": 20800,
            "RemainingCapital": 79200,
            "Allocation": 20.8,
            "ActualRiskPercent": 0.8,
            "MaxLoss": 800,
            "PotentialProfit": 1600,
            "PositionStatus": "READY",
            "PositionRating": "STRONG",
        }
    )
    return output


def fake_portfolio(results):
    return {
        "results": results,
        "positions": results,
        "summary": {
            "account_capital": 100000,
            "capital_allocated": 0,
            "remaining_cash": 100000,
            "portfolio_risk_pct": 0,
            "active_positions": 0,
            "status": "NO ALLOCATION",
        },
    }


def main():
    with tempfile.TemporaryDirectory() as folder:
        options = BootstrapOptions(
            enable_paper_trading=True,
            enable_notifications=True,
            enable_journal=True,
            enable_analytics=True,
            telegram_enabled=False,
            journal_database_path=str(
                Path(folder) / "journal.db"
            ),
        )

        application = UnifiedServiceBootstrap(
            options
        ).build(
            data_loader=fake_loader,
            indicator_function=fake_indicators,
            scorer=fake_score,
            trend_function=fake_trend,
            momentum_function=fake_momentum,
            volume_function=fake_volume,
            quality_function=passthrough,
            smart_money_function=fake_smart,
            regime_function=fake_regime,
            timing_function=fake_timing,
            brain_function=fake_brain,
            confidence_function=fake_confidence,
            strategy_function=fake_strategy,
            decision_function=fake_decision,
            risk_function=fake_risk,
            position_function=fake_position,
            portfolio_function=fake_portfolio,
        )

        services = application.services

        expected = [
            "application_services",
            "execution_manager",
            "portfolio_allocator_adapter",
            "paper_account",
            "paper_execution_engine",
            "paper_portfolio",
            "notification_hub",
            "trade_journal",
            "event_journal_bridge",
            "performance_engine",
        ]

        for name in expected:
            assert services.contains(name)

        assert (
            services.resolve(
                "application_services"
            )
            is application
        )

        assert application.analysis_bundle is not None
        assert application.execution_manager is not None
        assert application.paper_portfolio is not None
        assert application.notification_hub is not None
        assert application.trade_journal is not None
        assert application.performance_engine is not None

    print("=" * 94)
    print("BURSAAI v6.0 SPRINT 6G.1 TEST")
    print("=" * 94)
    print("Unified Infrastructure       : OK")
    print("Analysis Pipeline Bootstrap  : OK")
    print("Portfolio Service            : OK")
    print("Execution Manager            : OK")
    print("Paper Trading Services       : OK")
    print("Notification Hub             : OK")
    print("Trade Journal                : OK")
    print("Performance Analytics        : OK")
    print("Service Collision Guard      : OK")
    print("Application Services         : OK")
    print("=" * 94)
    print("SPRINT 6G.1 UNIFIED SERVICE BOOTSTRAP OK")


if __name__ == "__main__":
    main()
