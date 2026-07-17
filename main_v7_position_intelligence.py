from __future__ import annotations

from pathlib import Path

from TradingIntelligence import (
    PositionCandidate,
    PositionIntelligenceConfig,
    PositionIntelligenceEngine,
    PositionIntelligenceReport,
    PositionRiskProfile,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def build_demo_candidates() -> list[PositionCandidate]:
    return [
        PositionCandidate(
            symbol="1295.KL",
            price=4.90,
            atr=0.12,
            final_score=86.0,
            confidence=88.0,
            signal="STRONG BUY",
            ml_probability=0.82,
            volatility_percent=2.1,
            sector="FINANCIAL",
            support_price=4.82,
            resistance_price=5.35,
        ),
        PositionCandidate(
            symbol="1155.KL",
            price=10.80,
            atr=0.22,
            final_score=78.0,
            confidence=81.0,
            signal="BUY",
            ml_probability=0.72,
            volatility_percent=2.4,
            sector="FINANCIAL",
            support_price=10.62,
            resistance_price=11.40,
        ),
        PositionCandidate(
            symbol="5347.KL",
            price=13.20,
            atr=0.35,
            final_score=62.0,
            confidence=66.0,
            signal="WATCH",
            ml_probability=0.54,
            volatility_percent=4.2,
            sector="UTILITIES",
            support_price=12.85,
            resistance_price=13.80,
        ),
    ]


def main() -> None:
    print("=" * 108)
    print(
        " BursaAI v7 Sprint 7C.1 — "
        "Institutional Position Intelligence Engine"
    )
    print("=" * 108)

    config = PositionIntelligenceConfig(
        portfolio_capital=100000.0,
    )

    profile = PositionRiskProfile(
        portfolio_capital=100000.0,
        available_capital=90000.0,
        current_portfolio_risk_percent=1.5,
        active_positions=2,
        current_drawdown_percent=2.0,
        sector_exposure_percent=18.0,
    )

    engine = PositionIntelligenceEngine(config)

    plans = [
        engine.build_plan(candidate, profile)
        for candidate in build_demo_candidates()
    ]

    print()
    print("POSITION INTELLIGENCE")
    print("-" * 108)

    for plan in plans:
        print(
            f"{plan.symbol:<10} "
            f"{plan.action:<24} "
            f"Approved={str(plan.approved):<5} "
            f"Q={plan.quality_score:>6.2f} "
            f"Entry={plan.entry_price:>7.3f} "
            f"SL={plan.stop_loss:>7.3f} "
            f"Target={plan.target_price:>7.3f} "
            f"RR={plan.risk_reward:>5.2f} "
            f"Qty={plan.quantity:>6} "
            f"Risk={plan.risk_percent:>5.2f}%"
        )

    outputs = PositionIntelligenceReport(
        PROJECT_ROOT
        / "Reports"
        / "PositionIntelligence"
    ).export(plans)

    print()
    print("OUTPUT FILES")
    print("-" * 108)

    for name, path in outputs.items():
        print(f"{name:<10}: {path}")

    print("=" * 108)
    print("SPRINT 7C.1 COMPLETED")
    print("=" * 108)


if __name__ == "__main__":
    main()
