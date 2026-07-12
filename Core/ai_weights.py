"""BursaAI AI Brain Weights - Version 5.3 Batch 5A."""
AI_WEIGHTS = {
    "trend": 0.18,
    "momentum": 0.14,
    "volume": 0.12,
    "smart_money": 0.12,
    "market_regime": 0.10,
    "multi_timeframe": 0.12,
    "entry_timing": 0.10,
    "trade_quality": 0.12,
}

CONVICTION_LEVELS = [
    (85, "INSTITUTIONAL CONVICTION"),
    (75, "HIGH CONVICTION"),
    (65, "MODERATE CONVICTION"),
    (50, "LOW CONVICTION"),
    (0, "NO CONVICTION"),
]

AI_SIGNAL_LEVELS = [
    (88, "STRONG CONVICTION BUY"),
    (78, "STRONG BUY"),
    (68, "BUY"),
    (55, "WATCH"),
    (40, "HOLD"),
    (0, "AVOID"),
]

AI_RISK_MULTIPLIER = {
    "INSTITUTIONAL CONVICTION": 1.10,
    "HIGH CONVICTION": 1.00,
    "MODERATE CONVICTION": 0.85,
    "LOW CONVICTION": 0.65,
    "NO CONVICTION": 0.00,
}
