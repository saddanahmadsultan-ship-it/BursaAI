"""
====================================================
BursaAI Configuration
Version : 5.0 Core Refactor Compatibility
====================================================
"""

# ==================================================
# SYSTEM
# ==================================================

SYSTEM_NAME = "BursaAI"
VERSION = "5.0"

EXPORT_FILE = "BursaAI_Report.xlsx"

MIN_REQUIRED_ROWS = 220

DEBUG_SCORE = False


# ==================================================
# CAPITAL / PORTFOLIO
# ==================================================

DEFAULT_CAPITAL = 100000.00
DEFAULT_RISK_PERCENT = 1.0
MAX_PORTFOLIO_RISK = 5.0
MAX_POSITION_PERCENT = 20.0
MIN_POSITION_PERCENT = 2.0

LOT_SIZE = 100
ROUND_LOT = True


# ==================================================
# STRATEGY / RISK REWARD
# ==================================================

DEFAULT_STOPLOSS_ATR = 2.0
DEFAULT_TARGET_ATR = 4.0

MIN_RR = 2.0

STRONG_BUY_SCORE = 80
BUY_SCORE = 75
WATCH_SCORE = 62
HOLD_SCORE = 50
AVOID_SCORE = 35

MAX_SCORE = 100


# ==================================================
# CONFIDENCE
# ==================================================

CONFIDENCE_HIGH = 70
CONFIDENCE_MEDIUM = 55
CONFIDENCE_LOW = 40


# ==================================================
# MOMENTUM ENGINE
# Maximum Score : 25
# ==================================================

MOMENTUM_RSI_STRONG = 8
MOMENTUM_RSI_GOOD = 6
MOMENTUM_RSI_FAIR = 4

MOMENTUM_MACD_BULLISH = 8
MOMENTUM_MACD_ABOVE_ZERO = 5

MOMENTUM_HISTOGRAM_POSITIVE = 2
MOMENTUM_ROC_POSITIVE = 2

MOMENTUM_RSI_HEALTHY = 50
MOMENTUM_RSI_RECOVERING = 45
MOMENTUM_RSI_WEAK = 40
MOMENTUM_RSI_OVERBOUGHT = 70
MOMENTUM_RSI_OVERSOLD = 30

MOMENTUM_STOCH_HEALTHY = 4
MOMENTUM_CCI_POSITIVE = 4


# ==================================================
# TREND ENGINE
# Maximum Score : 35
# ==================================================

TREND_EMA20_ABOVE_EMA50 = 8
TREND_EMA50_ABOVE_EMA200 = 7
TREND_PRICE_ABOVE_EMA20 = 3
TREND_PRICE_ABOVE_EMA50 = 2
TREND_PRICE_ABOVE_EMA200 = 2
TREND_EMA20_RISING = 3
TREND_HIGHER_HIGH = 2
TREND_HIGHER_LOW = 2
TREND_BULLISH_CANDLE = 2
TREND_ABOVE_VWAP = 2
TREND_BREAKOUT = 2
TREND_HEALTHY_DISTANCE = 2
TREND_EXTENDED_PENALTY = 2


# ==================================================
# VOLUME ENGINE
# Maximum Score : 15
# ==================================================

VOLUME_RVOL_EXCEPTIONAL = 2.5
VOLUME_RVOL_STRONG = 2.0
VOLUME_RVOL_ABOVE_AVERAGE = 1.5
VOLUME_RVOL_NORMAL = 1.0
VOLUME_RVOL_LOW = 0.5

VOLUME_SCORE_EXCEPTIONAL = 4
VOLUME_SCORE_STRONG = 3
VOLUME_SCORE_ABOVE_AVERAGE = 2
VOLUME_SCORE_NORMAL = 1

VOLUME_SCORE_OBV = 2
VOLUME_SCORE_CMF_STRONG = 2
VOLUME_SCORE_CMF_POSITIVE = 1
VOLUME_SCORE_MFI_HEALTHY = 2
VOLUME_SCORE_SMART_MONEY_STRONG = 3
VOLUME_SCORE_SMART_MONEY = 2
VOLUME_SCORE_EARLY_SMART_MONEY = 1

VOLUME_STRONG_RATIO = 1.5
VOLUME_HEALTHY_RATIO = 1.2
VOLUME_WEAK_RATIO = 0.8


# ==================================================
# VOLATILITY ENGINE
# Maximum Score : 10
# ==================================================

VOLATILITY_LOW = 10
VOLATILITY_MEDIUM = 8
VOLATILITY_HIGH = 4
VOLATILITY_EXTREME = 0


# ==================================================
# QUALITY GATE
# ==================================================

QUALITY_WEAK_VOLUME = 7
QUALITY_VERY_LOW_CONFIDENCE = 14
QUALITY_LOW_CONFIDENCE = 10
QUALITY_MEDIUM_CONFIDENCE = 5
QUALITY_DOWNTREND = 15
QUALITY_SIDEWAYS = 9
QUALITY_WEAK_UPTREND = 4
QUALITY_RATING_D = 5
QUALITY_RATING_C = 2
QUALITY_RR_LOW = 8
QUALITY_RR_MEDIUM = 3


# ==================================================
# SMART MONEY ENGINE
# ==================================================

SMART_VOLUME_EXPANSION = 8
SMART_STRONG_VOLUME = 6
SMART_ABOVE_AVERAGE_VOLUME = 3
SMART_DRYUP = 2
SMART_OBV = 3
SMART_OBV_RISING = 2
SMART_CMF_STRONG = 6
SMART_CMF = 4
SMART_VWAP = 3
SMART_HIGHER_LOW = 2
SMART_HIGHER_HIGH = 2
SMART_BREAKOUT = 5
SMART_MACD = 2
SMART_ROC = 1
SMART_ATR = 2


# ==================================================
# MARKET REGIME ENGINE
# ==================================================

REGIME_BULLISH = 40
REGIME_RECOVERY = 20
REGIME_SIDEWAYS = 5
REGIME_WEAK = -15


# ==================================================
# ENTRY TIMING ENGINE
# ==================================================

ENTRY_READY = 55
ENTRY_CONFIRM = 40
ENTRY_PULLBACK = 25


# ==================================================
# EXCEL / DASHBOARD
# ==================================================

TOP_PICKS = 5
MAX_EXCEL_COLUMN_WIDTH = 45