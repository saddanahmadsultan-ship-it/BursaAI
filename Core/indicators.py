"""
=========================================
BursaAI Indicator Engine
Version : 6.1 Stable Institutional Fix
=========================================
"""

import numpy as np
import pandas as pd


def calculate_obv(close, volume):

    obv = [0]

    for i in range(1, len(close)):

        if close.iloc[i] > close.iloc[i - 1]:
            obv.append(obv[-1] + volume.iloc[i])

        elif close.iloc[i] < close.iloc[i - 1]:
            obv.append(obv[-1] - volume.iloc[i])

        else:
            obv.append(obv[-1])

    return pd.Series(obv, index=close.index)


def add_indicators(df):

    if df is None or df.empty:
        return df

    required = ["Open", "High", "Low", "Close", "Volume"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df.copy()

    df["Volume"] = df["Volume"].fillna(0)

    # ==========================
    # MA / EMA
    # ==========================

    df["MA20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["MA200"] = df["Close"].rolling(200, min_periods=1).mean()

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    df["EMA20_SLOPE"] = df["EMA20"].diff().fillna(0)
    df["EMA50_SLOPE"] = df["EMA50"].diff().fillna(0)
    df["EMA200_SLOPE"] = df["EMA200"].diff().fillna(0)

    # ==========================
    # STRUCTURE
    # ==========================

    df["HIGHER_HIGH"] = df["High"] > df["High"].shift(1)
    df["HIGHER_LOW"] = df["Low"] > df["Low"].shift(1)
    df["LOWER_HIGH"] = df["High"] < df["High"].shift(1)
    df["LOWER_LOW"] = df["Low"] < df["Low"].shift(1)

    # ==========================
    # RSI
    # ==========================

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)

    # ==========================
    # MACD
    # ==========================

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]
    df["MACD_HISTOGRAM"] = df["MACD_HIST"]

    df["MACD_BULLISH"] = df["MACD"] > df["MACD_SIGNAL"]
    df["MACD_ABOVE_ZERO"] = df["MACD"] > 0

    # ==========================
    # MOMENTUM
    # ==========================

    df["ROC"] = ((df["Close"] - df["Close"].shift(10)) / df["Close"].shift(10)) * 100
    df["ROC"] = df["ROC"].fillna(0)

    low14 = df["Low"].rolling(14, min_periods=1).min()
    high14 = df["High"].rolling(14, min_periods=1).max()

    df["STOCH"] = ((df["Close"] - low14) / (high14 - low14).replace(0, np.nan)) * 100
    df["STOCH"] = df["STOCH"].fillna(50)

    tp = (df["High"] + df["Low"] + df["Close"]) / 3

    sma_tp = tp.rolling(20, min_periods=1).mean()

    mad = tp.rolling(20, min_periods=1).apply(
        lambda x: np.mean(np.abs(x - x.mean())),
        raw=True
    )

    df["CCI"] = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
    df["CCI"] = df["CCI"].fillna(0)

    # ==========================
    # BOLLINGER BAND
    # ==========================

    std20 = df["Close"].rolling(20, min_periods=1).std().fillna(0)

    df["BB_UPPER"] = df["MA20"] + (2 * std20)
    df["BB_LOWER"] = df["MA20"] - (2 * std20)

    # ==========================
    # ATR
    # ==========================

    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["ATR"] = tr.rolling(14, min_periods=1).mean()
    df["ATR"] = df["ATR"].fillna(0)

    df["ATR_PERCENT"] = (df["ATR"] / df["Close"].replace(0, np.nan)) * 100
    df["ATR_PERCENT"] = df["ATR_PERCENT"].fillna(0)

    # ==========================
    # VOLUME
    # ==========================

    df["VOL5"] = df["Volume"].rolling(5, min_periods=1).mean()
    df["VOL10"] = df["Volume"].rolling(10, min_periods=1).mean()
    df["VOL20"] = df["Volume"].rolling(20, min_periods=1).mean()
    df["VOL50"] = df["Volume"].rolling(50, min_periods=1).mean()

    df["VOL_EMA20"] = df["Volume"].ewm(span=20, adjust=False).mean()
    df["VOL_EMA50"] = df["Volume"].ewm(span=50, adjust=False).mean()

    df["VOL_RATIO"] = df["Volume"] / df["VOL20"].replace(0, np.nan)
    df["RVOL"] = df["VOL_RATIO"].fillna(0)

    df["RVOL5"] = df["Volume"] / df["VOL5"].replace(0, np.nan)
    df["RVOL5"] = df["RVOL5"].fillna(0)

    df["VOLUME_SPIKE"] = df["RVOL"] >= 2.0
    df["VOLUME_EXPANSION"] = df["RVOL"] >= 1.3
    df["VOLUME_CONTRACTION"] = df["RVOL"] < 0.8
    df["VOLUME_DRYUP"] = df["RVOL"] < 0.5

    # ==========================
    # OBV
    # ==========================

    df["OBV"] = calculate_obv(df["Close"], df["Volume"])

    df["OBV_MA20"] = df["OBV"].rolling(20, min_periods=1).mean()
    df["OBV_MA50"] = df["OBV"].rolling(50, min_periods=1).mean()

    df["OBV_BULLISH"] = df["OBV"] > df["OBV_MA20"]

    # ==========================
    # VWAP
    # ==========================

    typical = (df["High"] + df["Low"] + df["Close"]) / 3

    cum_vol = df["Volume"].cumsum()
    cum_tp = (typical * df["Volume"]).cumsum()

    df["VWAP"] = cum_tp / cum_vol.replace(0, np.nan)
    df["VWAP"] = df["VWAP"].fillna(df["Close"])

    df["ABOVE_VWAP"] = df["Close"] > df["VWAP"]

    # ==========================
    # MFI
    # ==========================

    raw_money_flow = typical * df["Volume"]
    tp_change = typical.diff()

    positive_flow = raw_money_flow.where(tp_change > 0, 0)
    negative_flow = raw_money_flow.where(tp_change < 0, 0).abs()

    positive_mf = positive_flow.rolling(14, min_periods=1).sum()
    negative_mf = negative_flow.rolling(14, min_periods=1).sum()

    money_ratio = positive_mf / negative_mf.replace(0, np.nan)

    df["MFI"] = 100 - (100 / (1 + money_ratio))
    df["MFI"] = df["MFI"].fillna(50)

    # ==========================
    # ADL / CMF
    # ==========================

    price_range = (df["High"] - df["Low"]).replace(0, np.nan)

    mf_multiplier = (
        ((df["Close"] - df["Low"]) - (df["High"] - df["Close"]))
        / price_range
    ).fillna(0)

    mf_volume = mf_multiplier * df["Volume"]

    df["ADL"] = mf_volume.cumsum()

    cmf_num = mf_volume.rolling(20, min_periods=1).sum()
    cmf_den = df["Volume"].rolling(20, min_periods=1).sum()

    df["CMF"] = cmf_num / cmf_den.replace(0, np.nan)
    df["CMF"] = df["CMF"].fillna(0)

    # ==========================
    # SMART MONEY
    # ==========================

    df["ACCUMULATION"] = (
        (df["CMF"] > 0)
        & (df["OBV_BULLISH"])
        & (df["RVOL"] >= 1)
    )

    df["DISTRIBUTION"] = (
        (df["CMF"] < 0)
        & (df["RVOL"] >= 1)
    )

    df["INSTITUTIONAL_BUY"] = (
        df["ACCUMULATION"]
        & (df["MFI"] > 55)
        & (df["Close"] > df["VWAP"])
    )

    df["INSTITUTIONAL_SELL"] = (
        df["DISTRIBUTION"]
        & (df["MFI"] < 45)
        & (df["Close"] < df["VWAP"])
    )

    smart_money = np.zeros(len(df))

    smart_money += np.where(df["INSTITUTIONAL_BUY"], 4, 0)
    smart_money += np.where(df["CMF"] > 0, 2, 0)
    smart_money += np.where(df["MFI"] > 60, 2, 0)
    smart_money += np.where(df["OBV_BULLISH"], 2, 0)
    smart_money -= np.where(df["INSTITUTIONAL_SELL"], 4, 0)

    df["SMART_MONEY_SCORE"] = smart_money

    df["SMART_MONEY_STRENGTH"] = np.select(
        [
            smart_money >= 8,
            smart_money >= 5,
            smart_money >= 2
        ],
        [
            "STRONG",
            "GOOD",
            "NORMAL"
        ],
        default="WEAK"
    )

    # ==========================
    # BREAKOUT
    # ==========================

    highest20 = df["High"].rolling(20, min_periods=1).max().shift(1)
    lowest20 = df["Low"].rolling(20, min_periods=1).min().shift(1)

    df["BREAKOUT"] = (
        (df["Close"] > highest20)
        & (df["RVOL"] >= 1.5)
    )

    df["BREAKDOWN"] = df["Close"] < lowest20

    df["FAKE_BREAKOUT"] = df["BREAKOUT"] & (df["CMF"] < 0)

    # ==========================
    # QUALITY SCORES
    # ==========================

    df["TREND_SCORE"] = 0

    df["TREND_SCORE"] += np.where(df["EMA20"] > df["EMA50"], 2, 0)
    df["TREND_SCORE"] += np.where(df["EMA50"] > df["EMA200"], 2, 0)
    df["TREND_SCORE"] += np.where(df["Close"] > df["EMA20"], 2, 0)
    df["TREND_SCORE"] += np.where(df["HIGHER_HIGH"], 2, 0)
    df["TREND_SCORE"] += np.where(df["HIGHER_LOW"], 2, 0)

    df["MOMENTUM_SCORE"] = 0

    df["MOMENTUM_SCORE"] += np.where(df["RSI"] > 50, 2, 0)
    df["MOMENTUM_SCORE"] += np.where(df["MACD_BULLISH"], 2, 0)
    df["MOMENTUM_SCORE"] += np.where(df["MACD_ABOVE_ZERO"], 2, 0)
    df["MOMENTUM_SCORE"] += np.where(df["ROC"] > 0, 2, 0)
    df["MOMENTUM_SCORE"] += np.where(df["CCI"] > 0, 2, 0)

    df["VOLUME_SCORE"] = 0

    df["VOLUME_SCORE"] += np.where(df["RVOL"] >= 2.0, 4, 0)
    df["VOLUME_SCORE"] += np.where(df["RVOL"] >= 1.3, 2, 0)
    df["VOLUME_SCORE"] += np.where(df["OBV_BULLISH"], 2, 0)
    df["VOLUME_SCORE"] += np.where(df["ABOVE_VWAP"], 2, 0)
    df["VOLUME_SCORE"] += np.where(df["INSTITUTIONAL_BUY"], 3, 0)
    df["VOLUME_SCORE"] -= np.where(df["VOLUME_DRYUP"], 2, 0)

    df["VOLATILITY_SCORE"] = np.select(
        [
            df["ATR_PERCENT"] < 2,
            df["ATR_PERCENT"] < 4,
            df["ATR_PERCENT"] < 6
        ],
        [
            4,
            3,
            2
        ],
        default=1
    )

    df["TREND_LABEL"] = np.select(
        [
            df["TREND_SCORE"] >= 8,
            df["TREND_SCORE"] >= 6,
            df["TREND_SCORE"] >= 4
        ],
        [
            "STRONG UPTREND",
            "UPTREND",
            "SIDEWAYS"
        ],
        default="DOWNTREND"
    )

    df["MOMENTUM_STRENGTH"] = np.select(
        [
            df["MOMENTUM_SCORE"] >= 8,
            df["MOMENTUM_SCORE"] >= 6,
            df["MOMENTUM_SCORE"] >= 4
        ],
        [
            "STRONG",
            "GOOD",
            "NORMAL"
        ],
        default="WEAK"
    )

    df["VOLUME_STRENGTH"] = np.select(
        [
            df["VOLUME_SCORE"] >= 9,
            df["VOLUME_SCORE"] >= 6,
            df["VOLUME_SCORE"] >= 3
        ],
        [
            "STRONG",
            "GOOD",
            "NORMAL"
        ],
        default="WEAK"
    )

    df["VOLATILITY_LABEL"] = np.select(
        [
            df["VOLATILITY_SCORE"] >= 4,
            df["VOLATILITY_SCORE"] >= 3,
            df["VOLATILITY_SCORE"] >= 2
        ],
        [
            "LOW",
            "NORMAL",
            "HIGH"
        ],
        default="EXTREME"
    )

    df["AI_QUALITY_SCORE"] = (
        df["TREND_SCORE"]
        + df["MOMENTUM_SCORE"]
        + df["VOLUME_SCORE"]
        + df["SMART_MONEY_SCORE"]
    )

    # ==========================
    # FINAL CLEANUP
    # ==========================

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    df[numeric_cols] = (
        df[numeric_cols]
        .bfill()
        .ffill()
        .fillna(0)
    )

    bool_cols = df.select_dtypes(include=["bool"]).columns

    df[bool_cols] = df[bool_cols].fillna(False)

    object_cols = df.select_dtypes(include=["object"]).columns

    df[object_cols] = df[object_cols].fillna("UNKNOWN")

    return df