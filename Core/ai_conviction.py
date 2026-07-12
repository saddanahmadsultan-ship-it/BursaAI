"""BursaAI AI Conviction Calculator - Version 5.3 Batch 5A."""
from Core.ai_weights import AI_WEIGHTS, CONVICTION_LEVELS, AI_SIGNAL_LEVELS


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value, low=0.0, high=100.0):
    return max(low, min(safe_float(value), high))


def normalize_engine_score(data, fallback=50.0):
    if not isinstance(data, dict):
        return fallback
    value = data.get("score", data.get("value", fallback))
    value = safe_float(value, fallback)
    # Most BursaAI sub-engine scores are below 40.
    if value <= 40:
        value *= 2.5
    return clamp(value)


def label_from_levels(score, levels):
    for minimum, label in levels:
        if score >= minimum:
            return label
    return levels[-1][1]


def calculate_conviction(components):
    total = 0.0
    contributions = {}
    for name, weight in AI_WEIGHTS.items():
        score = clamp(components.get(name, 50.0))
        contribution = score * weight
        contributions[name] = round(contribution, 2)
        total += contribution
    total = round(clamp(total), 2)
    return {
        "score": total,
        "level": label_from_levels(total, CONVICTION_LEVELS),
        "signal": label_from_levels(total, AI_SIGNAL_LEVELS),
        "contributions": contributions,
    }
