"""
=========================================================
BursaAI Entry Timing Configuration
Version : 5.1 Batch 4A
=========================================================
"""

READY_SCORE = 70.0
EARLY_SCORE = 55.0
WAIT_SCORE = 40.0

IDEAL_RSI_MIN = 45.0
IDEAL_RSI_MAX = 68.0
OVERBOUGHT_RSI = 72.0

IDEAL_STOCH_MIN = 20.0
IDEAL_STOCH_MAX = 82.0
OVERBOUGHT_STOCH = 88.0

MAX_EXTENSION_ATR = 1.75

TIMING_RISK_MULTIPLIER = {
    "READY": 1.00,
    "EARLY": 0.75,
    "WAIT": 0.50,
    "AVOID": 0.00,
    "UNKNOWN": 0.00,
}
