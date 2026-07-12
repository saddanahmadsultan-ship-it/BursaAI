"""
=========================================
BursaAI Report Engine
Version : 2.0 (Hybrid)
=========================================

Terminal + Structured Report + AI Ready Output
"""


def generate_report(data, score_data, strategy_data, confidence):

    last = data.iloc[-1]

    close = float(last["Close"])

    trend = score_data["trend"]
    momentum = score_data["momentum"]
    volume = score_data["volume"]
    volatility = score_data["volatility"]

    rr = strategy_data.get("rr", 0)

    # ==========================
    # TEXT REPORT (Terminal)
    # ==========================

    report_text = []

    report_text.append("=" * 60)
    report_text.append("            BURSAAI AI REPORT")
    report_text.append("=" * 60)

    report_text.append(f"Price        : RM {close:.2f}")
    report_text.append(f"Score        : {score_data['score']} / 85")
    report_text.append(f"Confidence   : {confidence['confidence']}% ({confidence['level']})")

    report_text.append("")
    report_text.append(f"Trend        : {trend['quality']} ({trend['score']}/30)")
    report_text.append(f"Momentum     : {momentum['quality']} ({momentum['score']}/25)")
    report_text.append(f"Volume       : {volume['quality']} ({volume['score']}/20)")
    report_text.append(f"Volatility   : {volatility['quality']} ({volatility['score']}/10)")

    report_text.append("")
    report_text.append(f"Signal       : {strategy_data['strategy']}")
    report_text.append(f"Entry        : RM {strategy_data['entry']:.2f}")
    report_text.append(f"Stop Loss    : RM {strategy_data['stoploss']:.2f}")
    report_text.append(f"Target       : RM {strategy_data['target']:.2f}")
    report_text.append(f"Risk Reward  : 1:{rr}")

    report_text.append("")
    report_text.append("AI Summary")
    report_text.append("-" * 30)

    # placeholder (brain akan generate nanti)
    report_text.append("Generated in main.py via ai_summary()")

    report_text.append("")
    report_text.append("=" * 60)

    # ==========================
    # STRUCTURED DATA (EXPORT READY)
    # ==========================

    report_data = {

        "price": close,

        "score": score_data["score"],
        "confidence": confidence["confidence"],
        "confidence_level": confidence["level"],

        "trend_score": trend["score"],
        "momentum_score": momentum["score"],
        "volume_score": volume["score"],
        "volatility_score": volatility["score"],

        "trend_quality": trend["quality"],
        "momentum_quality": momentum["quality"],
        "volume_quality": volume["quality"],
        "volatility_quality": volatility["quality"],

        "strategy": strategy_data["strategy"],
        "entry": strategy_data["entry"],
        "stoploss": strategy_data["stoploss"],
        "target": strategy_data["target"],
        "risk_reward": rr,

        "bullish": strategy_data["bullish"],

        "warnings": strategy_data["warning"],

        "trend_reason": trend["reason"],
        "momentum_reason": momentum["reason"],
        "volume_reason": volume["reason"],
        "volatility_reason": volatility["reason"]

    }

    return {
        "text": "\n".join(report_text),
        "data": report_data
    }