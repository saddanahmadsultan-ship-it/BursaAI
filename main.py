"""
====================================================
BursaAI AI Dashboard
Version : 5.3 Batch 5A Institutional AI Brain
====================================================
"""

from Core.stock_loader import load_stock_list
from Core.data_loader import load_stock
from Core.indicators import add_indicators

from Core.scorer import calculate_score
from Core.confidence import calculate_confidence
from Core.strategy import trading_signal
from Core.decision import make_decision

from Core.exporter import export_excel
from Core.validator import validate_trade
from Core.ai_modifier import apply_ai_modifier
from Core.config import MIN_REQUIRED_ROWS

from Core.quality_gate import apply_quality_gate
from Core.smart_money_engine import apply_smart_money_engine
from Core.market_regime_engine import apply_market_regime_engine
from Core.entry_timing_engine import apply_entry_timing_engine
from Core.ai_brain import apply_ai_brain
from Core.dynamic_risk_manager import apply_dynamic_risk_manager
from Core.position_engine import apply_position_engine
from Core.portfolio_allocator import (
    allocate_portfolio,
    print_portfolio_positions,
    print_portfolio_summary
)

from Core.result_model import (
    build_result,
    sync_result_structure
)


print("=" * 70)
print("       BURSAAI AI DASHBOARD v5.3 BATCH 5A")
print("=" * 70)


stocks = load_stock_list()

print(f"\nTotal saham : {len(stocks)}\n")

results = []


for i, symbol in enumerate(stocks, start=1):

    print(
        f"[{i}/{len(stocks)}] "
        f"Scanning {symbol}..."
    )

    try:

        # =====================================
        # LOAD DATA
        # =====================================

        data = load_stock(symbol)

        if data is None or data.empty:
            print("Tiada data.")
            continue

        if len(data) < MIN_REQUIRED_ROWS:
            print(
                f"Data tidak cukup ({len(data)} baris). "
                f"Minimum {MIN_REQUIRED_ROWS} baris diperlukan."
            )
            continue

        data = add_indicators(data)

        if data is None or data.empty:
            print("Indicator data tidak tersedia.")
            continue

        last = data.iloc[-1]

        # =====================================
        # AI SCORE
        # =====================================

        score_data = calculate_score(data)

        trend_data = score_data["trend"]
        momentum_data = score_data["momentum"]
        volume_data = score_data["volume"]
        volatility_data = score_data["volatility"]
        risk_data = score_data["risk"]

        # =====================================
        # AI MODIFIER
        # =====================================

        modifier_data = apply_ai_modifier(
            trend_data,
            momentum_data,
            volume_data,
            volatility_data,
            risk_data
        )

        # =====================================
        # CONFIDENCE
        # =====================================

        confidence = calculate_confidence(
            trend_data,
            momentum_data,
            volume_data,
            volatility_data,
            risk_data,
            modifier_data
        )

        # =====================================
        # STRATEGY
        # =====================================

        strategy_data = trading_signal(
            data,
            score_data,
            trend_data,
            momentum_data,
            volume_data,
            confidence
        )

        # =====================================
        # DECISION INPUT
        # =====================================

        decision_input = {
            "score": score_data["score"],

            "price": float(
                last["Close"]
            ),

            "ema20": float(
                last["EMA20"]
            ),

            "ema50": float(
                last["EMA50"]
            ),

            "ema200": float(
                last["EMA200"]
            ),

            "ema20_slope": float(
                last["EMA20_SLOPE"]
            ),

            "higher_high": bool(
                last["HIGHER_HIGH"]
            ),

            "higher_low": bool(
                last["HIGHER_LOW"]
            ),

            "lower_high": bool(
                last["LOWER_HIGH"]
            ),

            "breakout": bool(
                last["BREAKOUT"]
            ),

            "breakdown": bool(
                last["BREAKDOWN"]
            ),

            "vwap": float(
                last["VWAP"]
            ),

            "rsi": float(
                last["RSI"]
            ),

            "macd": float(
                last["MACD"]
            ),

            "macd_signal":
                "Bullish"
                if float(last["MACD"]) >=
                float(last["MACD_SIGNAL"])
                else "Bearish",

            "macd_histogram": float(
                last["MACD_HISTOGRAM"]
            ),

            "roc": float(
                last["ROC"]
            ),

            "stoch": float(
                last["STOCH"]
            ),

            "cci": float(
                last["CCI"]
            ),

            "volume_score":
                volume_data["score"],

            "obv_bullish":
                float(last["OBV"]) >
                float(last["OBV_MA20"]),

            "atr_percent": float(
                last["ATR_PERCENT"]
            ),

            "confidence":
                confidence["confidence"],

            "rr":
                strategy_data["rr"],

            "trend":
                trend_data["direction"]
        }

        # =====================================
        # AI DECISION
        # =====================================

        decision_data = make_decision(
            decision_input
        )

        # =====================================
        # VALIDATION
        # =====================================

        validator = validate_trade(
            trend_data,
            momentum_data,
            volume_data,
            confidence,
            strategy_data,
            decision_data
        )

        # =====================================
        # RESULT MODEL
        # =====================================

        result = build_result(
            symbol=symbol,
            last=last,
            score_data=score_data,
            trend_data=trend_data,
            momentum_data=momentum_data,
            volume_data=volume_data,
            volatility_data=volatility_data,
            risk_data=risk_data,
            confidence_data=confidence,
            strategy_data=strategy_data,
            decision_data=decision_data,
            validator=validator
        )

        # =====================================
        # QUALITY GATE
        # =====================================

        result = apply_quality_gate(result)

        result = sync_result_structure(
            result
        )

        # =====================================
        # SMART MONEY
        # =====================================

        result = apply_smart_money_engine(
            data,
            result
        )

        result = sync_result_structure(
            result
        )

        # =====================================
        # MARKET REGIME
        # =====================================

        result = apply_market_regime_engine(
            data,
            result
        )

        result = sync_result_structure(
            result
        )

        # =====================================
        # ENTRY TIMING ENGINE
        # =====================================

        result = apply_entry_timing_engine(
            data,
            result
        )

        result = sync_result_structure(
            result
        )

        # =====================================
        # INSTITUTIONAL AI BRAIN
        # =====================================

        result = apply_ai_brain(result)

        result = sync_result_structure(
            result
        )

        # =====================================
        # DYNAMIC RISK MANAGER
        # =====================================

        result = apply_dynamic_risk_manager(
            result
        )

        result = sync_result_structure(
            result
        )

        # =====================================
        # POSITION SIZING
        # =====================================

        result = apply_position_engine(
            result
        )

        result = sync_result_structure(
            result
        )

        results.append(result)

    except Exception as error:

        print(
            f"[ERROR] {symbol}: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        continue


# =====================================
# SORT
# =====================================

results.sort(
    key=lambda item: item.get(
        "FinalScore",
        item.get("Score", 0)
    ),
    reverse=True
)


# =====================================
# PORTFOLIO ALLOCATION ENGINE
# BATCH 3D
# =====================================

portfolio_data = allocate_portfolio(results)
results = portfolio_data["results"]
portfolio_summary = portfolio_data["summary"]

print_portfolio_positions(portfolio_data)
print_portfolio_summary(portfolio_data)


# =====================================
# EXPORT
# =====================================

export_excel(
    results,
    portfolio_summary=portfolio_summary
)


# =====================================
# RANKING DASHBOARD
# =====================================

print("\n")
print("=" * 225)
print("                         AI RANKING DASHBOARD")
print("=" * 225)

print(
    f"{'Rank':<6}"
    f"{'Code':<10}"
    f"{'Price':>9}"
    f"{'Raw':>7}"
    f"{'T.Score':>9}"
    f"{'Final':>8}"
    f"{'Grade':>8}"
    f"{'Conf':>9}"
    f"{'Market':>12}"
    f"{'Signal':>12}"
    f"{'Lots':>8}"
    f"{'Shares':>10}"
    f"{'Capital':>14}"
    f"{'Alloc%':>9}"
    f"{'MaxLoss':>12}"
    f"{'Profit':>13}"
    f"{'Position Status':>22}"
    f"{'Rating':>12}"
)

print("-" * 225)


for rank, item in enumerate(
    results,
    start=1
):

    identity = item["identity"]
    score = item["score"]
    confidence_data = item["confidence"]
    market = item["market"]
    trade = item["trade"]
    position = item["position"]

    print(
        f"{rank:<6}"
        f"{identity['code']:<10}"
        f"{identity['price']:>9.2f}"
        f"{score['raw']:>7}"
        f"{score['tradeable']:>9}"
        f"{score['final']:>8}"
        f"{score['grade']:>8}"
        f"{confidence_data['value']:>9.1f}"
        f"{market['regime']:>12}"
        f"{trade['signal']:>12}"
        f"{position['lots']:>8}"
        f"{position['shares']:>10}"
        f"{position['capital_used']:>14.2f}"
        f"{position['allocation_percent']:>9.2f}"
        f"{position['max_loss']:>12.2f}"
        f"{position['potential_profit']:>13.2f}"
        f"{position['status']:>22}"
        f"{position['rating']:>12}"
    )


# =====================================
# DETAILED REPORT
# =====================================

print("\n")
print("=" * 225)
print("                         AI DETAILED REPORT")
print("=" * 225)


for item in results:

    identity = item["identity"]
    score = item["score"]
    confidence_data = item["confidence"]
    market = item["market"]
    trade = item["trade"]
    position = item["position"]
    analysis = item["analysis"]

    print("\n" + "=" * 85)

    print(
        f"CODE              : "
        f"{identity['code']}"
    )

    print(
        f"PRICE             : RM "
        f"{identity['price']:.2f}"
    )

    print(
        f"RAW SCORE         : "
        f"{score['raw']}"
    )

    print(
        f"QUALITY PENALTY   : "
        f"{score['quality_penalty']}"
    )

    print(
        f"TRADEABLE SCORE   : "
        f"{score['tradeable']}"
    )

    print(
        f"INSTITUTION BONUS : "
        f"{score['institution_bonus']}"
    )

    print(
        f"REGIME SCORE      : "
        f"{market['regime_score']}"
    )

    print(
        f"REGIME BONUS      : "
        f"{score['regime_bonus']}"
    )

    print(
        f"REGIME PENALTY    : "
        f"{score['regime_penalty']}"
    )

    print(
        f"FINAL SCORE       : "
        f"{score['final']}"
    )

    print(
        f"GRADE             : "
        f"{score['grade']}"
    )

    print(
        f"CONFIDENCE        : "
        f"{confidence_data['value']}% "
        f"({confidence_data['level']})"
    )

    print(
        f"TREND             : "
        f"{market['trend']}"
    )

    print(
        f"VOLUME            : "
        f"{market['volume']}"
    )

    print(
        f"SMART MONEY       : "
        f"{market['smart_money']}"
    )

    print(
        f"MARKET REGIME     : "
        f"{market['regime']}"
    )

    print(
        f"SIGNAL            : "
        f"{trade['signal']}"
    )

    print(
        f"AI RATING         : "
        f"{trade['rating']}"
    )

    print()

    print("-" * 85)
    print("TRADE PLAN")
    print("-" * 85)

    print(
        f"ENTRY             : RM "
        f"{trade['entry']:.2f}"
    )

    print(
        f"STOP LOSS         : RM "
        f"{trade['stop_loss']:.2f}"
    )

    print(
        f"TARGET            : RM "
        f"{trade['target']:.2f}"
    )

    print(
        f"RISK REWARD       : "
        f"{trade['risk_reward']:.2f}"
    )

    print()

    timing = item.get("entry_timing", {})

    print("-" * 85)
    print("ENTRY TIMING")
    print("-" * 85)

    print(
        f"TIMING SCORE      : "
        f"{timing.get('score', 0):.2f}"
    )

    print(
        f"TIMING STATUS     : "
        f"{timing.get('status', 'UNKNOWN')}"
    )

    print(
        f"TIMING ACTION     : "
        f"{timing.get('action', 'NO ACTION')}"
    )

    print(
        f"ENTRY ZONE        : RM "
        f"{timing.get('entry_zone_low', 0):.2f} - RM "
        f"{timing.get('entry_zone_high', 0):.2f}"
    )

    print()

    ai_brain = item.get("ai_brain", {})
    ai_reasoning = ai_brain.get("reasoning", {})

    print("-" * 85)
    print("INSTITUTIONAL AI BRAIN")
    print("-" * 85)
    print(f"AI CONVICTION      : {ai_brain.get('conviction_score', 0):.2f}/100")
    print(f"CONVICTION LEVEL   : {ai_brain.get('conviction_level', 'UNKNOWN')}")
    print(f"AI SIGNAL          : {ai_brain.get('ai_signal', 'UNKNOWN')}")
    print(f"PREDICTION STABILITY: {ai_brain.get('prediction_stability', 0):.2f}%")
    print(f"EXECUTION QUALITY  : {ai_brain.get('execution_quality', 0):.2f}%")
    print(f"AI SUMMARY         : {ai_reasoning.get('summary', '')}")
    if ai_reasoning.get("strengths"):
        print("AI STRENGTHS")
        for text in ai_reasoning["strengths"]:
            print(f"  [PLUS] {text}")
    if ai_reasoning.get("weaknesses"):
        print("AI WEAKNESSES")
        for text in ai_reasoning["weaknesses"]:
            print(f"  [MINUS] {text}")
    print()

    dynamic_risk = item.get("dynamic_risk", {})
    multipliers = dynamic_risk.get("multipliers", {})

    print("-" * 85)
    print("DYNAMIC RISK MANAGER")
    print("-" * 85)

    print(
        f"BASE RISK         : "
        f"{dynamic_risk.get('base_risk_percent', 0):.2f}%"
    )
    print(
        f"FINAL RISK        : "
        f"{dynamic_risk.get('final_risk_percent', 0):.2f}%"
    )
    print(
        f"RISK STATUS       : "
        f"{dynamic_risk.get('status', 'UNKNOWN')}"
    )
    print(
        f"COMBINED MULTIPLIER: "
        f"{dynamic_risk.get('combined_multiplier', 0):.4f}"
    )
    print(
        f"REGIME / VOL      : "
        f"{multipliers.get('regime', 0):.2f} / "
        f"{multipliers.get('volatility', 0):.2f}"
    )
    print(
        f"CONF / SCORE      : "
        f"{multipliers.get('confidence', 0):.2f} / "
        f"{multipliers.get('score', 0):.2f}"
    )
    print(
        f"RISK REASON       : "
        f"{dynamic_risk.get('reason', '')}"
    )

    print()

    print("-" * 85)
    print("POSITION SIZING")
    print("-" * 85)

    print(
        f"ACCOUNT CAPITAL   : RM "
        f"{position['account_capital']:.2f}"
    )

    print(
        f"RISK PERCENT      : "
        f"{position['risk_percent']:.2f}%"
    )

    print(
        f"RISK CAPITAL      : RM "
        f"{position['risk_capital']:.2f}"
    )

    print(
        f"RISK PER SHARE    : RM "
        f"{position['risk_per_share']:.2f}"
    )

    print(
        f"SUGGESTED SHARES  : "
        f"{position['shares']}"
    )

    print(
        f"SUGGESTED LOTS    : "
        f"{position['lots']}"
    )

    print(
        f"CAPITAL USED      : RM "
        f"{position['capital_used']:.2f}"
    )

    print(
        f"REMAINING CAPITAL : RM "
        f"{position['remaining_capital']:.2f}"
    )

    print(
        f"ALLOCATION        : "
        f"{position['allocation_percent']:.2f}%"
    )

    print(
        f"ACTUAL RISK       : "
        f"{position['actual_risk_percent']:.2f}%"
    )

    print(
        f"MAXIMUM LOSS      : RM "
        f"{position['max_loss']:.2f}"
    )

    print(
        f"POTENTIAL PROFIT  : RM "
        f"{position['potential_profit']:.2f}"
    )

    print(
        f"POSITION STATUS   : "
        f"{position['status']}"
    )

    print(
        f"POSITION RATING   : "
        f"{position['rating']}"
    )

    portfolio = item.get("portfolio", {})

    print()
    print("-" * 85)
    print("PORTFOLIO ALLOCATION")
    print("-" * 85)

    print(
        f"PORTFOLIO STATUS  : "
        f"{portfolio.get('status', 'SKIP')}"
    )
    print(
        f"PORTFOLIO REASON  : "
        f"{portfolio.get('reason', '')}"
    )
    print(
        f"ALLOCATED SHARES  : "
        f"{portfolio.get('allocated_shares', 0)}"
    )
    print(
        f"ALLOCATED LOTS    : "
        f"{portfolio.get('allocated_lots', 0)}"
    )
    print(
        f"ALLOCATED CAPITAL : RM "
        f"{portfolio.get('allocated_capital', 0):.2f}"
    )
    print(
        f"PORTFOLIO RISK    : RM "
        f"{portfolio.get('allocated_max_loss', 0):.2f} "
        f"({portfolio.get('risk_percent', 0):.2f}%)"
    )
    print(
        f"CASH AFTER        : RM "
        f"{portfolio.get('remaining_cash_after', 0):.2f}"
    )

    print()

    print("-" * 85)
    print("AI DECISION")
    print("-" * 85)

    print(
        analysis["summary"]
    )

    print()

    print("AI ANALYSIS")

    if analysis["reasons"]:

        for reason in analysis["reasons"]:

            print(
                f"  [INFO] {reason}"
            )

    else:

        print("  - No analysis.")

    print()

    print("RISK WARNING")

    if analysis["warnings"]:

        for warning in analysis["warnings"]:

            print(
                f"  [WARN] {warning}"
            )

    else:

        print("  None")

    print("=" * 85)


# =====================================
# TOP PICKS
# =====================================

print("\n")
print("=" * 120)
print("TOP ALLOCATED PORTFOLIO POSITIONS")
print("=" * 120)

top = [
    item
    for item in results
    if item.get(
        "PortfolioStatus",
        item.get("portfolio", {}).get(
            "status",
            "SKIP"
        )
    ) in {"ALLOCATED", "REDUCED"}
][:5]

if not top:

    print("Tiada posisi portfolio yang dialokasikan.")

else:

    for rank, item in enumerate(
        top,
        start=1
    ):

        identity = item["identity"]
        score = item["score"]
        market = item["market"]
        trade = item["trade"]
        position = item["position"]
        confidence_data = item["confidence"]

        print(
            f"{rank}. "
            f"{identity['code']}"
            f" | Final {score['final']}"
            f" | {trade['signal']}"
            f" | {market['regime']}"
            f" | Lots {item.get('portfolio', {}).get('allocated_lots', 0)}"
            f" | Capital RM{item.get('portfolio', {}).get('allocated_capital', 0):.2f}"
            f" | MaxLoss RM{item.get('portfolio', {}).get('allocated_max_loss', 0):.2f}"
            f" | Profit RM{item.get('portfolio', {}).get('allocated_potential_profit', 0):.2f}"
            f" | {item.get('portfolio', {}).get('status', 'SKIP')}"
            f" | Confidence "
            f"{confidence_data['value']}%"
            f" | AI {item.get('AIConviction', 0):.0f}"
            f" {item.get('AIConvictionLevel', 'UNKNOWN')}"
        )


# =====================================
# END
# =====================================