"""
=========================================================
BursaAI Dynamic Risk Configuration
Version : 5.2 Batch 4B
=========================================================
"""

MIN_DYNAMIC_RISK_PERCENT = 0.15
MAX_DYNAMIC_RISK_PERCENT = 1.20

RISK_STATUS_THRESHOLD = {
    "NORMAL RISK": 0.70,
    "REDUCED RISK": 0.35,
    "MINIMUM RISK": 0.01,
}

REGIME_MULTIPLIER = {
    "BULLISH": 1.10,
    "RECOVERY": 0.90,
    "SIDEWAYS": 0.65,
    "WEAK": 0.40,
    "BEARISH": 0.00,
    "UNKNOWN": 0.50,
}

VOLATILITY_MULTIPLIER = {
    "LOW": 1.05,
    "HEALTHY": 1.00,
    "STABLE": 1.00,
    "NORMAL": 1.00,
    "MEDIUM": 0.90,
    "HIGH": 0.65,
    "EXTREME": 0.35,
    "UNKNOWN": 0.85,
}

CONFIDENCE_BANDS = (
    (85.0, 1.10),
    (75.0, 1.00),
    (65.0, 0.85),
    (55.0, 0.65),
    (0.0, 0.00),
)

SCORE_BANDS = (
    (85.0, 1.10),
    (75.0, 1.00),
    (65.0, 0.85),
    (55.0, 0.65),
    (0.0, 0.00),
)

RR_BANDS = (
    (3.00, 1.10),
    (2.00, 1.00),
    (1.70, 0.90),
    (1.50, 0.75),
    (0.00, 0.00),
)

SMART_MONEY_MULTIPLIER = {
    "STRONG": 1.10,
    "ACCUMULATION": 1.08,
    "CONFIRMED": 1.05,
    "EARLY": 1.00,
    "NEUTRAL": 0.90,
    "NONE": 0.85,
    "DISTRIBUTION": 0.50,
    "UNKNOWN": 0.85,
}