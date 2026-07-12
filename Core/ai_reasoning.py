"""BursaAI Explainable AI Reasoning - Version 5.3 Batch 5A."""

def build_reasoning(components, result, conviction):
    strengths, weaknesses = [], []
    labels = {
        "trend": "Trend structure",
        "momentum": "Momentum",
        "volume": "Volume participation",
        "smart_money": "Smart-money activity",
        "market_regime": "Market regime",
        "multi_timeframe": "Multi-timeframe alignment",
        "entry_timing": "Entry timing",
        "trade_quality": "Trade quality",
    }
    for key, label in labels.items():
        value = float(components.get(key, 50))
        if value >= 70:
            strengths.append(f"{label} is strong ({value:.0f}/100)")
        elif value < 45:
            weaknesses.append(f"{label} is weak ({value:.0f}/100)")

    signal = str(result.get("Signal", "UNKNOWN"))
    regime = str(result.get("MarketRegime", "UNKNOWN"))
    timing = str(result.get("EntryTimingStatus", "UNKNOWN"))
    summary = (
        f"AI conviction {conviction['score']:.0f}/100 ({conviction['level']}). "
        f"Current signal {signal}, regime {regime}, timing {timing}. "
        f"AI action: {conviction['signal']}."
    )
    return {"summary": summary, "strengths": strengths, "weaknesses": weaknesses}
