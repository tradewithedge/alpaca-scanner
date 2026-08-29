from __future__ import annotations

import math
import re
from typing import Iterable, Optional

import numpy as np
import pandas as pd


INSPECTOR_VERSION = "V1.2.1.2"


def symbol_key(symbol: str) -> str:
    """Canonical comparison key used only for matching symbols."""
    return "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())


def normalize_ticker(value: str) -> str:
    """Normalize a user-entered ticker without silently changing its identity."""
    value = str(value or "").strip().upper()
    value = re.sub(r"\s+", "", value)
    if not value:
        return ""
    # Common U.S.-equity symbol characters. The canonical key is used only
    # when resolving against Alpaca/source-universe symbols.
    if not re.fullmatch(r"[A-Z0-9.\-]{1,15}", value):
        return ""
    return value


def resolve_asset(assets: Iterable[dict], query: str) -> Optional[dict]:
    """Resolve exact symbol first, then canonical symbol equivalence."""
    query = normalize_ticker(query)
    if not query:
        return None

    assets = list(assets or [])
    for asset in assets:
        if str(asset.get("symbol", "")).upper() == query:
            return asset

    qkey = symbol_key(query)
    matches = [
        asset
        for asset in assets
        if symbol_key(asset.get("symbol", "")) == qkey
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def in_selected_universe(symbol: str, selected_symbols) -> Optional[bool]:
    """Return None for an unrestricted All-U.S. universe."""
    if selected_symbols is None:
        return None
    target = symbol_key(symbol)
    return target in {symbol_key(s) for s in selected_symbols}


def pct_rank_against_reference(value, reference) -> float:
    """Match legacy scanner pandas rank(pct=True)*100 semantics."""
    if value is None or pd.isna(value):
        return np.nan
    ref = pd.to_numeric(pd.Series(reference), errors="coerce").dropna()
    combined = pd.concat(
        [ref.reset_index(drop=True), pd.Series([float(value)])],
        ignore_index=True,
    )
    return float(combined.rank(method="average", pct=True).iloc[-1] * 100.0)


def zero_to_100_rank_against_reference(value, reference) -> float:
    """Match the V1.2.1 leadership 0..100 percentile convention."""
    if value is None or pd.isna(value):
        return np.nan
    ref = pd.to_numeric(pd.Series(reference), errors="coerce").dropna()
    combined = pd.concat(
        [ref.reset_index(drop=True), pd.Series([float(value)])],
        ignore_index=True,
    )
    n = len(combined)
    if n == 1:
        return 50.0
    rank = float(combined.rank(method="average", ascending=True).iloc[-1])
    return float(np.clip(100.0 * (rank - 1.0) / (n - 1.0), 0.0, 100.0))


def liquidity_diagnostic(bar: dict | None, min_price: float, min_dollar_volume: float) -> dict:
    """Explain previous-session price/liquidity gates for one ticker."""
    bar = bar or {}
    px = bar.get("c")
    vol = bar.get("v")
    ts = bar.get("t")

    try:
        px = float(px)
        vol = float(vol)
    except Exception:
        return {
            "status": "UNKNOWN",
            "reason": "No usable completed-session SIP bar.",
            "prev_close": np.nan,
            "previous_volume": np.nan,
            "prev_dollar_volume": np.nan,
            "bar_timestamp": ts,
        }

    if not math.isfinite(px) or not math.isfinite(vol) or px <= 0 or vol < 0:
        return {
            "status": "UNKNOWN",
            "reason": "Completed-session SIP bar is not usable.",
            "prev_close": px,
            "previous_volume": vol,
            "prev_dollar_volume": np.nan,
            "bar_timestamp": ts,
        }

    dollar_volume = px * vol
    failures = []
    if px < float(min_price):
        failures.append(f"price below ${float(min_price):.2f}")
    if dollar_volume < float(min_dollar_volume):
        failures.append("previous-session dollar volume below cutoff")

    return {
        "status": "PASS" if not failures else "FAIL",
        "reason": "All initial liquidity gates passed." if not failures else "; ".join(failures),
        "prev_close": px,
        "previous_volume": vol,
        "prev_dollar_volume": dollar_volume,
        "bar_timestamp": ts,
    }
