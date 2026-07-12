"""
=========================================================
BursaAI Portfolio Configuration
Version : 5.0 Professional
Batch   : 3D Stable
=========================================================
"""

# =========================================================
# ACCOUNT CAPITAL
# =========================================================

ACCOUNT_CAPITAL = 100_000.00


# =========================================================
# POSITION ENGINE SETTINGS
# =========================================================

RISK_PER_TRADE_PCT = 1.00
MAX_POSITION_PCT = 25.00
MIN_POSITION_PCT = 3.00
MIN_FINAL_SCORE = 65.00
MIN_CONFIDENCE = 65.00
MIN_RISK_REWARD_RATIO = 1.50
BOARD_LOT_SIZE = 100
ROUND_TO_BOARD_LOT = True

SIGNAL_RISK_MULTIPLIER = {
    "STRONG CONVICTION BUY": 1.20,
    "STRONG BUY": 1.00,
    "BUY": 0.85,
    "ACCUMULATE": 0.75,
    "WATCH": 0.50,
    "HOLD": 0.00,
    "AVOID": 0.00,
    "UNKNOWN": 0.00,
}


# =========================================================
# PORTFOLIO ALLOCATION SETTINGS
# =========================================================

MAX_PORTFOLIO_RISK_PCT = 5.00
CASH_RESERVE_PCT = 10.00
MAX_ACTIVE_POSITIONS = 5

ALLOWED_SIGNALS = {
    "STRONG CONVICTION BUY",
    "STRONG BUY",
    "BUY",
    "ACCUMULATE",
    "WATCH",
}

STATUS_ALLOCATED = "ALLOCATED"
STATUS_REDUCED = "REDUCED"
STATUS_SKIP = "SKIP"
STATUS_NO_CAPITAL = "NO CAPITAL"


def get_portfolio_config():
    """Return one configuration dictionary for all portfolio modules."""

    return {
        # Position engine keys
        "capital": ACCOUNT_CAPITAL,
        "risk_percent": RISK_PER_TRADE_PCT,
        "max_position_percent": MAX_POSITION_PCT,
        "min_position_percent": MIN_POSITION_PCT,
        "lot_size": BOARD_LOT_SIZE,
        "round_lot": ROUND_TO_BOARD_LOT,
        "minimum_final_score": MIN_FINAL_SCORE,
        "minimum_confidence": MIN_CONFIDENCE,
        "minimum_risk_reward": MIN_RISK_REWARD_RATIO,
        "signal_risk_multiplier": dict(SIGNAL_RISK_MULTIPLIER),

        # Portfolio allocator keys
        "max_portfolio_risk_percent": MAX_PORTFOLIO_RISK_PCT,
        "cash_reserve_percent": CASH_RESERVE_PCT,
        "max_active_positions": MAX_ACTIVE_POSITIONS,
        "allowed_signals": set(ALLOWED_SIGNALS),
    }