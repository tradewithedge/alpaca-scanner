from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd


AUDIT_REQUIRED_COLUMNS = [
    "symbol",
    "outcome_state",
    "fill_status",
    "realized_r",
    "net_realized_r",
    "missed_opportunity_r",
    "mae_r",
    "mfe_r",
    "fill_slippage_r",
    "commission_cash",
]


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _validate(outcomes: pd.DataFrame | None) -> pd.DataFrame:
    if outcomes is None or outcomes.empty:
        return pd.DataFrame(columns=AUDIT_REQUIRED_COLUMNS)
    missing = [c for c in AUDIT_REQUIRED_COLUMNS if c not in outcomes.columns]
    if missing:
        raise ValueError(f"outcomes missing required columns: {missing}")
    return outcomes.copy(deep=True)


def _max_drawdown_r(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for value in values:
        equity += float(value)
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)
    return float(max_dd)


def summarize_audit_metrics(outcomes: pd.DataFrame | None) -> dict:
    """Compute descriptive V1.7 audit/expectancy metrics.

    This function is deliberately descriptive. It does not estimate statistical
    significance, confidence intervals, or out-of-sample performance.
    """
    frame = _validate(outcomes)
    if frame.empty:
        return {
            "signals": 0,
            "triggered": 0,
            "filled": 0,
            "realized": 0,
            "missed": 0,
            "no_fill": 0,
            "entry_rate_pct": 0.0,
            "capture_rate_pct": 0.0,
            "realization_rate_pct": 0.0,
            "fill_rate_pct": 0.0,
            "win_rate_pct": None,
            "loss_rate_pct": None,
            "mean_realized_r": None,
            "mean_net_realized_r": None,
            "signal_expectancy_r": 0.0,
            "mean_missed_opportunity_r": 0.0,
            "total_missed_opportunity_r": 0.0,
            "mean_mae_r": None,
            "mean_mfe_r": None,
            "mean_fill_slippage_r": None,
            "total_commission_cash": 0.0,
            "max_drawdown_r": 0.0,
            "audit_all_no_lookahead": True,
            "audit_all_timestamps_strict": True,
            "audit_all_deterministic": True,
        }

    states = frame["outcome_state"].astype(str)
    filled = frame["fill_status"].astype(str).str.upper().eq("FILLED")
    realized = _numeric(frame["realized_r"])
    net = _numeric(frame["net_realized_r"])
    missed = _numeric(frame["missed_opportunity_r"]).fillna(0.0)
    mae = _numeric(frame["mae_r"])
    mfe = _numeric(frame["mfe_r"])
    slippage = _numeric(frame["fill_slippage_r"])
    commission = _numeric(frame["commission_cash"]).fillna(0.0)

    realized_net = net[filled & net.notna()]
    triggered = frame["trigger_timestamp_utc"].astype(str).str.strip().ne("") if "trigger_timestamp_utc" in frame.columns else states.ne("TRIGGER_NOT_REACHED")
    missed_count = int((missed > 0).sum())
    triggered_count = int(triggered.sum())

    wins = int((realized_net > 0).sum())
    losses = int((realized_net <= 0).sum())
    filled_count = int(filled.sum())
    signal_count = int(len(frame))
    realized_count = int(realized[realized.notna() & filled].shape[0])

    mean_net = None if realized_net.empty else float(realized_net.mean())
    signal_expectancy = 0.0 if mean_net is None else float(realized_net.sum() / signal_count)

    audit_no_lookahead = frame["audit_no_lookahead"].fillna(False).astype(bool) if "audit_no_lookahead" in frame.columns else pd.Series(True, index=frame.index)
    audit_timestamps = frame["audit_timestamps_strict"].fillna(False).astype(bool) if "audit_timestamps_strict" in frame.columns else pd.Series(True, index=frame.index)
    audit_deterministic = frame["audit_deterministic"].fillna(False).astype(bool) if "audit_deterministic" in frame.columns else pd.Series(True, index=frame.index)

    return {
        "signals": signal_count,
        "triggered": triggered_count,
        "filled": filled_count,
        "realized": realized_count,
        "missed": missed_count,
        "no_fill": int((~filled).sum()),
        "entry_rate_pct": float(100.0 * triggered_count / signal_count),
        "capture_rate_pct": 0.0 if triggered_count == 0 else float(100.0 * filled_count / triggered_count),
        "realization_rate_pct": 0.0 if filled_count == 0 else float(100.0 * realized_count / filled_count),
        "fill_rate_pct": float(100.0 * filled_count / signal_count),
        "win_rate_pct": None if realized_net.empty else float(100.0 * wins / len(realized_net)),
        "loss_rate_pct": None if realized_net.empty else float(100.0 * losses / len(realized_net)),
        "mean_realized_r": None if realized[filled & realized.notna()].empty else float(realized[filled & realized.notna()].mean()),
        "mean_net_realized_r": mean_net,
        "signal_expectancy_r": signal_expectancy,
        "mean_missed_opportunity_r": float(missed.mean()),
        "total_missed_opportunity_r": float(missed.sum()),
        "mean_mae_r": None if mae.dropna().empty else float(mae.mean()),
        "mean_mfe_r": None if mfe.dropna().empty else float(mfe.mean()),
        "mean_fill_slippage_r": None if slippage.dropna().empty else float(slippage.mean()),
        "total_commission_cash": float(commission.sum()),
        "max_drawdown_r": _max_drawdown_r(realized_net.tolist()),
        "audit_all_no_lookahead": bool(audit_no_lookahead.all()),
        "audit_all_timestamps_strict": bool(audit_timestamps.all()),
        "audit_all_deterministic": bool(audit_deterministic.all()),
    }


def segment_audit_metrics(
    outcomes: pd.DataFrame | None,
    by: str | Iterable[str],
) -> pd.DataFrame:
    """Summarize metrics by one or more explicit segmentation fields."""
    frame = _validate(outcomes)
    fields = [by] if isinstance(by, str) else list(by)
    missing = [field for field in fields if field not in frame.columns]
    if missing:
        raise ValueError(f"segmentation columns missing: {missing}")
    if frame.empty:
        return pd.DataFrame(columns=[*fields, "signals", "filled", "signal_expectancy_r"])

    rows: list[dict] = []
    for keys, group in frame.groupby(fields, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {field: value for field, value in zip(fields, keys)}
        row.update(summarize_audit_metrics(group))
        rows.append(row)
    return pd.DataFrame(rows)


__all__ = [
    "AUDIT_REQUIRED_COLUMNS",
    "segment_audit_metrics",
    "summarize_audit_metrics",
]
