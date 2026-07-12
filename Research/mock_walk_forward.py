from __future__ import annotations

import hashlib
from datetime import date, timedelta

from Research.candidate import Candidate


def deterministic_mock_walk_forward(
    candidate: Candidate,
):
    """
    Mock Walk Forward untuk validasi integrasi sahaja.
    Bukan backtest sebenar.
    """

    digest = hashlib.sha256(
        candidate.candidate_hash.encode("utf-8")
    ).hexdigest()

    seed = int(digest[:12], 16)

    cagr = 8.0 + (seed % 2200) / 100.0
    sharpe = 0.6 + ((seed // 7) % 210) / 100.0
    max_dd = 6.0 + ((seed // 11) % 1800) / 100.0
    win_rate = 40.0 + ((seed // 13) % 2500) / 100.0
    profit_factor = 1.0 + ((seed // 17) % 130) / 100.0

    final_score = min(
        100.0,
        cagr * 1.2
        + sharpe * 12.0
        + max(0.0, 25.0 - max_dd)
        + win_rate * 0.25
        + profit_factor * 8.0,
    )

    folds = []

    for fold_number in range(1, 6):
        folds.append(
            {
                "fold": fold_number,
                "train_return": round(
                    cagr * (0.8 + fold_number * 0.03),
                    2,
                ),
                "test_return": round(
                    cagr * (0.55 + fold_number * 0.025),
                    2,
                ),
                "test_sharpe": round(
                    sharpe * (
                        0.75 + fold_number * 0.04
                    ),
                    2,
                ),
            }
        )

    equity_curve = []
    value = 100000.0
    start = date(2024, 1, 1)

    for index in range(24):
        value *= (
            1.0
            + (
                cagr / 100.0
            ) / 24.0
        )

        equity_curve.append(
            {
                "date": (
                    start
                    + timedelta(days=index * 30)
                ).isoformat(),
                "equity": round(value, 2),
            }
        )

    return {
        "metrics": {
            "cagr": cagr,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "total_trades": 40 + seed % 120,
            "consistency_score": 70 + seed % 25,
            "robustness_score": 68 + seed % 27,
            "final_score": final_score,
        },
        "folds": folds,
        "monthly_returns": {
            "2024-01": 1.2,
            "2024-02": 0.8,
            "2024-03": 1.5,
        },
        "yearly_returns": {
            "2024": round(cagr * 0.85, 2),
            "2025": round(cagr * 1.05, 2),
        },
        "equity_curve": equity_curve,
        "trade_summary": {
            "average_holding_days": 12,
            "largest_win": 9.4,
            "largest_loss": -4.2,
        },
        "diagnostics": {
            "engine": "deterministic_mock",
            "fold_count": len(folds),
        },
    }
