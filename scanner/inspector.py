from __future__ import annotations

import math
import re
from typing import Iterable, Optional

import numpy as np
import pandas as pd


INSPECTOR_VERSION = "V1.2.1.3b1"


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



def inspector_authority(
    has_reference: bool,
    persistent_pass,
    liquidity_status: str,
    bucket: str | None = None,
) -> dict:
    """Return the authoritative UI state for Ticker Inspector outputs.

    A completed scanner cross-section is mandatory before percentile-dependent
    Candidate Quality, Leadership Score/Grade, persistent-quality eligibility,
    or an official scanner bucket may be presented as authoritative.
    """
    if not has_reference:
        return {
            "persistent_quality": "REF REQUIRED",
            "candidate_quality_authoritative": False,
            "leadership_authoritative": False,
            "legacy_rs_authoritative": False,
            "official_status": "NOT RANKED",
            "conclusion": "DIRECT DIAGNOSTICS",
        }

    persistent_label = "PASS" if persistent_pass is True else "FAIL"
    eligible = liquidity_status == "PASS" and persistent_pass is True

    return {
        "persistent_quality": persistent_label,
        "candidate_quality_authoritative": True,
        "leadership_authoritative": True,
        "legacy_rs_authoritative": True,
        "official_status": str(bucket or "ELIGIBLE") if eligible else "NOT ELIGIBLE",
        "conclusion": "ELIGIBLE" if eligible else "NOT ELIGIBLE",
    }


AUTO_REFERENCE_LABEL = "AUTO — Current selected universe"


def resolve_reference_universe(
    current_universe: str,
    reference_choice: str | None,
) -> str:
    """Resolve AUTO to the current scanner universe; otherwise use override."""
    choice = str(reference_choice or AUTO_REFERENCE_LABEL).strip()
    if not choice or choice == AUTO_REFERENCE_LABEL:
        return str(current_universe)
    return choice


def reference_signature(
    universe_name: str,
    min_price: float,
    min_prev_dollar_volume: float,
    max_deep_scan_symbols: int,
    history_days: int,
) -> tuple:
    """Stable identity for the peer population used by cross-sectional scores."""
    return (
        str(universe_name),
        round(float(min_price), 6),
        round(float(min_prev_dollar_volume), 2),
        int(max_deep_scan_symbols),
        int(history_days),
    )


def scan_reference_compatible(
    scan: dict | None,
    requested_universe: str,
    requested_signature: tuple,
) -> bool:
    """A completed scan is reusable only when its peer population is identical."""
    if not scan:
        return False
    cross = scan.get("cross_section")
    if cross is None or getattr(cross, "empty", True):
        return False
    if str(scan.get("universe_name", "")) != str(requested_universe):
        return False
    return tuple(scan.get("reference_signature", ())) == tuple(requested_signature)


def reference_coverage(reference_count: int, deep_scan_count: int) -> float:
    if not deep_scan_count:
        return 0.0
    return float(reference_count) / float(deep_scan_count)


def reference_confidence(reference_count: int, deep_scan_count: int) -> str:
    """Confidence in the cross-sectional peer distribution itself."""
    coverage = reference_coverage(reference_count, deep_scan_count)
    if reference_count >= 20 and coverage >= 0.95:
        return "HIGH"
    if reference_count >= 20 and coverage >= 0.90:
        return "MEDIUM"
    return "LOW"


def reference_is_usable(reference_count: int, deep_scan_count: int) -> bool:
    """Hard integrity gate for decision-grade percentile scoring."""
    return (
        int(reference_count) >= 20
        and reference_coverage(reference_count, deep_scan_count) >= 0.90
    )


def inspector_state_on_scanner_run(
    current_input: str,
    remembered_ticker: str,
    previously_requested: bool,
) -> dict:
    """Preserve a visible ticker inspector across a scanner rerun.

    The current sidebar value is authoritative when present. This avoids
    relying on a transient request flag during a long Streamlit rerun.
    """
    current = normalize_ticker(current_input)
    remembered = normalize_ticker(remembered_ticker)
    ticker = current or remembered

    # A visible ticker means the user wants that Inspector available after
    # Run Scanner. Otherwise preserve an already-requested remembered ticker.
    requested = bool(ticker and (current or previously_requested))

    return {
        "ticker": ticker,
        "requested": requested,
        "expanded": False,
    }

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
