import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    g = df.sort_values("timestamp").copy()
    g["ema8"] = g["close"].ewm(span=8, adjust=False).mean()
    g["ema20"] = g["close"].ewm(span=20, adjust=False).mean()
    g["ma50"] = g["close"].rolling(50).mean()
    g["ma200"] = g["close"].rolling(200).mean()

    pc = g["close"].shift(1)
    tr = pd.concat(
        [
            (g["high"] - g["low"]),
            (g["high"] - pc).abs(),
            (g["low"] - pc).abs(),
        ],
        axis=1,
    ).max(axis=1)

    g["atr14"] = tr.rolling(14).mean()
    g["atr_pct"] = 100 * g["atr14"] / g["close"].replace(0, np.nan)
    g["ret5"] = g["close"].pct_change(5)
    g["ret20"] = g["close"].pct_change(20)
    g["ret50"] = g["close"].pct_change(50)

    g["dollar_volume"] = g["close"] * g["volume"]

    # Persistent liquidity quality must be based on PRIOR completed sessions.
    # Excluding the current bar prevents a partial intraday daily bar from
    # artificially depressing 20D average volume and dollar volume.
    prior_volume = g["volume"].shift(1)
    prior_dollar_volume = g["dollar_volume"].shift(1)
    g["avg_vol20"] = prior_volume.rolling(20).mean()
    g["avg_dollar_volume20"] = prior_dollar_volume.rolling(20).mean()
    g["median_dollar_volume20"] = prior_dollar_volume.rolling(20).median()

    # Current-session participation versus the prior 20-session baseline.
    g["vol_ratio"] = g["volume"] / g["avg_vol20"].replace(0, np.nan)

    g["range5"] = (
        g["high"].rolling(5).max() - g["low"].rolling(5).min()
    ) / g["close"]
    g["range20"] = (
        g["high"].rolling(20).max() - g["low"].rolling(20).min()
    ) / g["close"]
    g["atr5"] = tr.rolling(5).mean()
    g["atr20"] = tr.rolling(20).mean()
    g["high20_prev"] = g["high"].shift(1).rolling(20).max()
    g["low10"] = g["low"].rolling(10).min()
    g["ma20_slope5"] = g["ema20"].pct_change(5)
    g["ma50_slope10"] = g["ma50"].pct_change(10)
    g["ma200_slope20"] = g["ma200"].pct_change(20)
    return g


def latest_snapshot(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    g = add_indicators(df)
    r = g.iloc[-1].to_dict()
    c = r.get("close")
    r["ext_ema8_pct"] = (
        100 * (c / r["ema8"] - 1)
        if c and pd.notna(r.get("ema8"))
        else None
    )
    r["ext_ema20_pct"] = (
        100 * (c / r["ema20"] - 1)
        if c and pd.notna(r.get("ema20"))
        else None
    )
    r["ext_atr"] = (
        (c - r["ema20"]) / r["atr14"]
        if (
            c
            and pd.notna(r.get("ema20"))
            and pd.notna(r.get("atr14"))
            and r["atr14"] > 0
        )
        else None
    )
    return r
