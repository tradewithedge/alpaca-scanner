from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import math

import pandas as pd


BACKTEST_OUTCOME_COLUMNS = [
    "symbol",
    "signal_timestamp_utc",
    "trigger_price",
    "entry_zone_low",
    "entry_zone_high",
    "max_acceptable_fill",
    "stop_price",
    "t1_price",
    "t2_price",
    "horizon_bars",
    "outcome_state",
    "trigger_timestamp_utc",
    "fill_status",
    "fill_timestamp_utc",
    "fill_price",
    "fill_slippage_pct",
    "fill_slippage_r",
    "invalidation_timestamp_utc",
    "invalidation_reason",
    "t1_timestamp_utc",
    "exit_timestamp_utc",
    "exit_price",
    "exit_reason",
    "realized_r",
    "net_realized_r",
    "mae_pct",
    "mfe_pct",
    "mae_r",
    "mfe_r",
    "bars_to_trigger",
    "bars_to_fill",
    "bars_to_exit",
    "missed_opportunity_r",
    "commission_cash",
    "position_size",
    "no_fill_reason",
    "audit_no_lookahead",
    "audit_timestamps_strict",
    "audit_deterministic",
    "audit_notes",
]


@dataclass(frozen=True)
class BacktestConfig:
    """Deterministic V1.7 Stage-1 benchmark assumptions.

    This is a validation-layer configuration. It does not alter the frozen
    scanner decision logic and does not place broker orders.
    """

    horizon_bars: int = 20
    same_bar_priority: str = "STOP"
    commission_per_side_cash: float = 0.0
    position_size: float = 1.0

    def __post_init__(self) -> None:
        if self.horizon_bars <= 0:
            raise ValueError("horizon_bars must be > 0")
        if self.same_bar_priority not in {"STOP", "TARGET"}:
            raise ValueError("same_bar_priority must be STOP or TARGET")
        if self.commission_per_side_cash < 0:
            raise ValueError("commission_per_side_cash must be >= 0")
        if self.position_size <= 0:
            raise ValueError("position_size must be > 0")


@dataclass(frozen=True)
class BacktestOutcome:
    symbol: str
    signal_timestamp_utc: str
    trigger_price: float | None
    entry_zone_low: float | None
    entry_zone_high: float | None
    max_acceptable_fill: float | None
    stop_price: float | None
    t1_price: float | None
    t2_price: float | None
    horizon_bars: int
    outcome_state: str
    trigger_timestamp_utc: str
    fill_status: str
    fill_timestamp_utc: str
    fill_price: float | None
    fill_slippage_pct: float | None
    fill_slippage_r: float | None
    invalidation_timestamp_utc: str
    invalidation_reason: str
    t1_timestamp_utc: str
    exit_timestamp_utc: str
    exit_price: float | None
    exit_reason: str
    realized_r: float | None
    net_realized_r: float | None
    mae_pct: float | None
    mfe_pct: float | None
    mae_r: float | None
    mfe_r: float | None
    bars_to_trigger: int | None
    bars_to_fill: int | None
    bars_to_exit: int | None
    missed_opportunity_r: float | None
    commission_cash: float
    position_size: float
    no_fill_reason: str
    audit_no_lookahead: bool
    audit_timestamps_strict: bool
    audit_deterministic: bool
    audit_notes: str

    def to_dict(self) -> dict:
        return asdict(self)


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _utc(value: object) -> pd.Timestamp | None:
    try:
        ts = pd.Timestamp(value)
    except Exception:
        return None
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _iso(ts: pd.Timestamp | None) -> str:
    if ts is None:
        return ""
    return ts.astimezone(timezone.utc).isoformat()


def _prepare_bars(bars: pd.DataFrame) -> tuple[pd.DataFrame, bool, str]:
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"bars missing required columns: {missing}")

    g = bars.copy(deep=True)
    g["_ts"] = pd.to_datetime(g["timestamp"], utc=True, errors="coerce")
    if g["_ts"].isna().any():
        raise ValueError("bars contain invalid timestamps")
    strict = bool(g["_ts"].is_unique)
    if not strict:
        raise ValueError("bars contain duplicate timestamps")

    g = g.sort_values("_ts").reset_index(drop=True)
    numeric = g[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise ValueError("bars contain non-numeric OHLC values")
    g[["open", "high", "low", "close"]] = numeric
    return g, strict, "Bars sorted by timestamp; duplicate timestamps rejected."


def _validate_plan(signal: pd.Series) -> tuple[dict, str | None]:
    required = [
        "trigger_price",
        "max_acceptable_fill",
        "stop_price",
        "t2_price",
    ]
    missing = [c for c in required if not _finite(signal.get(c))]
    if missing:
        return {}, f"missing/invalid plan fields: {', '.join(missing)}"

    vals = {c: float(signal.get(c)) for c in required}
    optional = ["entry_zone_low", "entry_zone_high", "t1_price"]
    for c in optional:
        vals[c] = float(signal.get(c)) if _finite(signal.get(c)) else None

    if vals["trigger_price"] <= vals["stop_price"]:
        return {}, "trigger_price must be greater than stop_price"
    if vals["max_acceptable_fill"] < vals["trigger_price"]:
        return {}, "max_acceptable_fill must be >= trigger_price"
    if vals["t2_price"] <= vals["trigger_price"]:
        return {}, "t2_price must be greater than trigger_price"

    return vals, None


def _empty_outcome(
    signal: pd.Series,
    cfg: BacktestConfig,
    *,
    state: str,
    reason: str = "",
    invalidation_ts: str = "",
    audit_no_lookahead: bool = True,
    audit_timestamps_strict: bool = True,
    audit_notes: str = "",
) -> BacktestOutcome:
    plan, _ = _validate_plan(signal)
    return BacktestOutcome(
        symbol=_text(signal.get("symbol")).upper(),
        signal_timestamp_utc=_iso(_utc(signal.get("signal_timestamp_utc"))),
        trigger_price=plan.get("trigger_price"),
        entry_zone_low=plan.get("entry_zone_low"),
        entry_zone_high=plan.get("entry_zone_high"),
        max_acceptable_fill=plan.get("max_acceptable_fill"),
        stop_price=plan.get("stop_price"),
        t1_price=plan.get("t1_price"),
        t2_price=plan.get("t2_price"),
        horizon_bars=cfg.horizon_bars,
        outcome_state=state,
        trigger_timestamp_utc="",
        fill_status="NO_FILL",
        fill_timestamp_utc="",
        fill_price=None,
        fill_slippage_pct=None,
        fill_slippage_r=None,
        invalidation_timestamp_utc=invalidation_ts,
        invalidation_reason=reason if state == "INVALIDATED_BEFORE_TRIGGER" else "",
        t1_timestamp_utc="",
        exit_timestamp_utc="",
        exit_price=None,
        exit_reason="",
        realized_r=None,
        net_realized_r=None,
        mae_pct=None,
        mfe_pct=None,
        mae_r=None,
        mfe_r=None,
        bars_to_trigger=None,
        bars_to_fill=None,
        bars_to_exit=None,
        missed_opportunity_r=0.0,
        commission_cash=0.0,
        position_size=cfg.position_size,
        no_fill_reason=reason,
        audit_no_lookahead=audit_no_lookahead,
        audit_timestamps_strict=audit_timestamps_strict,
        audit_deterministic=True,
        audit_notes=audit_notes,
    )


def evaluate_signal(
    signal: pd.Series,
    bars: pd.DataFrame,
    *,
    config: BacktestConfig | None = None,
) -> BacktestOutcome:
    """Evaluate one long-side signal using only bars strictly after signal time.

    Deterministic rules:
    - The signal bar itself is never eligible for trigger/fill/exit.
    - A trigger is observed when future high >= trigger.
    - A gap-open at/above trigger fills at the open only when open <= max fill.
    - A gap-open above max fill is a NO FILL; it is never back-filled.
    - Before trigger, a bar whose low <= stop invalidates the setup.
    - Once filled, if stop and T2 are both touched in one bar, the configured
      same-bar priority decides the outcome (default STOP).
    - T1 is recorded diagnostically but does not close the benchmark position.
    - If neither stop nor T2 occurs within the horizon, the trade exits at the
      final horizon close (TIMEOUT).
    """
    cfg = config or BacktestConfig()

    if signal is None:
        raise ValueError("signal is required")
    if bars is None or bars.empty:
        raise ValueError("bars are required")

    prepared, strict_ts, prep_note = _prepare_bars(bars)

    signal_ts = _utc(signal.get("signal_timestamp_utc"))
    if signal_ts is None:
        raise ValueError("signal_timestamp_utc is invalid")

    plan, plan_error = _validate_plan(signal)
    if plan_error:
        raise ValueError(plan_error)

    future = prepared[prepared["_ts"] > signal_ts].copy().reset_index(drop=True)
    audit_no_lookahead = True

    symbol = _text(signal.get("symbol")).upper()
    if future.empty:
        return _empty_outcome(
            signal,
            cfg,
            state="NO_FUTURE_BARS",
            reason="No bar exists strictly after signal timestamp.",
            audit_no_lookahead=audit_no_lookahead,
            audit_timestamps_strict=strict_ts,
            audit_notes=prep_note,
        )

    future = future.iloc[: cfg.horizon_bars].copy().reset_index(drop=True)

    trigger_ts = None
    fill_ts = None
    fill_price = None
    invalidation_ts = None
    t1_ts = None
    exit_ts = None
    exit_price = None
    exit_reason = ""
    outcome_state = "TRIGGER_NOT_REACHED"
    no_fill_reason = ""
    bars_to_trigger = None
    bars_to_fill = None
    bars_to_exit = None

    for i, row in future.iterrows():
        o, h, l, c = map(float, [row["open"], row["high"], row["low"], row["close"]])
        ts = row["_ts"]

        if fill_price is None:
            trigger_touched = h >= plan["trigger_price"]
            stop_touched = l <= plan["stop_price"]

            # A clean gap-open inside the permitted fill cap is an unambiguous
            # fill at the opening price. This must be recognized before any
            # same-bar low/stop ambiguity is considered.
            if o >= plan["trigger_price"] and o <= plan["max_acceptable_fill"]:
                trigger_ts = ts
                fill_ts = ts
                fill_price = o
                bars_to_trigger = i + 1
                bars_to_fill = i + 1

            elif o > plan["max_acceptable_fill"]:
                # A gap beyond the cap is a clean no-fill. Do not retroactively
                # fill after a later retracement in the same bar.
                if trigger_touched:
                    trigger_ts = ts
                    bars_to_trigger = i + 1
                    outcome_state = "NO_FILL_GAP_ABOVE_MAX"
                    no_fill_reason = "Bar opened above maximum acceptable fill after/through trigger."
                    break
                continue

            else:
                # Pre-trigger invalidation. If trigger and stop are both touched
                # on the same bar before an unambiguous fill, STOP wins under the
                # default conservative ordering.
                if trigger_touched and stop_touched and cfg.same_bar_priority == "STOP":
                    invalidation_ts = ts
                    outcome_state = "INVALIDATED_BEFORE_TRIGGER"
                    no_fill_reason = "Trigger and stop were both touched in the same pre-fill bar; STOP priority applied."
                    break

                if stop_touched and not trigger_touched:
                    invalidation_ts = ts
                    outcome_state = "INVALIDATED_BEFORE_TRIGGER"
                    no_fill_reason = "Setup invalidated below structural stop before trigger."
                    break

                if trigger_touched:
                    trigger_ts = ts
                    fill_ts = ts
                    fill_price = plan["trigger_price"]
                    bars_to_trigger = i + 1
                    bars_to_fill = i + 1
                else:
                    continue

            # Filled. Continue into post-fill path on the same bar.
            # A gap through stop/target is executed at the open.
        else:
            pass

        if fill_price is not None:
            # T1 is a diagnostic milestone only.
            if t1_ts is None and plan.get("t1_price") is not None and h >= plan["t1_price"]:
                t1_ts = ts

            stop_hit = l <= plan["stop_price"]
            target_hit = h >= plan["t2_price"]

            # Opening gap through an exit level takes precedence over intraday
            # touch because the first tradable price is the open.
            if o <= plan["stop_price"]:
                exit_ts = ts
                exit_price = o
                exit_reason = "STOP_GAP"
            elif o >= plan["t2_price"]:
                exit_ts = ts
                exit_price = o
                exit_reason = "TARGET2_GAP"
            elif stop_hit and target_hit:
                exit_ts = ts
                exit_price = plan["stop_price"] if cfg.same_bar_priority == "STOP" else plan["t2_price"]
                exit_reason = "STOP_AND_TARGET_SAME_BAR"
            elif stop_hit:
                exit_ts = ts
                exit_price = plan["stop_price"]
                exit_reason = "STOP"
            elif target_hit:
                exit_ts = ts
                exit_price = plan["t2_price"]
                exit_reason = "TARGET2"

            if exit_ts is not None:
                bars_to_exit = i + 1
                outcome_state = "FILLED_TARGET2" if "TARGET2" in exit_reason else "FILLED_STOP"
                break

    if fill_price is None:
        # If trigger never occurred and no invalidation occurred, keep the
        # outcome explicitly neutral: no trade was executed.
        if outcome_state == "TRIGGER_NOT_REACHED":
            no_fill_reason = "Trigger not reached within the configured horizon."
        return BacktestOutcome(
            symbol=symbol,
            signal_timestamp_utc=_iso(signal_ts),
            trigger_price=plan["trigger_price"],
            entry_zone_low=plan.get("entry_zone_low"),
            entry_zone_high=plan.get("entry_zone_high"),
            max_acceptable_fill=plan["max_acceptable_fill"],
            stop_price=plan["stop_price"],
            t1_price=plan.get("t1_price"),
            t2_price=plan["t2_price"],
            horizon_bars=cfg.horizon_bars,
            outcome_state=outcome_state,
            trigger_timestamp_utc=_iso(trigger_ts),
            fill_status="NO_FILL",
            fill_timestamp_utc="",
            fill_price=None,
            fill_slippage_pct=None,
            fill_slippage_r=None,
            invalidation_timestamp_utc=_iso(invalidation_ts),
            invalidation_reason=no_fill_reason if outcome_state == "INVALIDATED_BEFORE_TRIGGER" else "",
            t1_timestamp_utc="",
            exit_timestamp_utc="",
            exit_price=None,
            exit_reason="",
            realized_r=None,
            net_realized_r=None,
            mae_pct=None,
            mfe_pct=None,
            mae_r=None,
            mfe_r=None,
            bars_to_trigger=bars_to_trigger,
            bars_to_fill=None,
            bars_to_exit=None,
            missed_opportunity_r=_missed_opportunity_r(
                future,
                plan,
                cfg,
                filled=False,
            ),
            commission_cash=0.0,
            position_size=cfg.position_size,
            no_fill_reason=no_fill_reason,
            audit_no_lookahead=audit_no_lookahead,
            audit_timestamps_strict=strict_ts,
            audit_deterministic=True,
            audit_notes=prep_note,
        )

    # Fill occurred. If no exit occurred during the normal loop, time out at
    # the final horizon close.
    if exit_ts is None:
        last = future.iloc[-1]
        exit_ts = last["_ts"]
        exit_price = float(last["close"])
        exit_reason = "TIMEOUT"
        outcome_state = "TIMEOUT"
        bars_to_exit = len(future)

    risk_per_unit = float(fill_price) - plan["stop_price"]
    if risk_per_unit <= 0:
        raise ValueError("filled trade has non-positive risk distance")

    realized_r = (float(exit_price) - float(fill_price)) / risk_per_unit
    commission_cash = 2.0 * cfg.commission_per_side_cash
    gross_trade_cash = realized_r * risk_per_unit * cfg.position_size
    net_trade_cash = gross_trade_cash - commission_cash
    net_realized_r = net_trade_cash / (risk_per_unit * cfg.position_size)

    fill_slippage_abs = float(fill_price) - plan["trigger_price"]
    fill_slippage_pct = 100.0 * fill_slippage_abs / plan["trigger_price"]
    fill_slippage_r = fill_slippage_abs / risk_per_unit

    # MAE/MFE use the bars from fill through exit inclusive.
    fill_idx = int(future.index[future["_ts"] == fill_ts][0])
    exit_idx = int(future.index[future["_ts"] == exit_ts][0])
    trade_bars = future.iloc[fill_idx : exit_idx + 1]
    lowest = float(trade_bars["low"].min())
    highest = float(trade_bars["high"].max())
    mae_pct = 100.0 * (lowest - float(fill_price)) / float(fill_price)
    mfe_pct = 100.0 * (highest - float(fill_price)) / float(fill_price)
    mae_r = (lowest - float(fill_price)) / risk_per_unit
    mfe_r = (highest - float(fill_price)) / risk_per_unit

    return BacktestOutcome(
        symbol=symbol,
        signal_timestamp_utc=_iso(signal_ts),
        trigger_price=plan["trigger_price"],
        entry_zone_low=plan.get("entry_zone_low"),
        entry_zone_high=plan.get("entry_zone_high"),
        max_acceptable_fill=plan["max_acceptable_fill"],
        stop_price=plan["stop_price"],
        t1_price=plan.get("t1_price"),
        t2_price=plan["t2_price"],
        horizon_bars=cfg.horizon_bars,
        outcome_state=outcome_state,
        trigger_timestamp_utc=_iso(trigger_ts),
        fill_status="FILLED",
        fill_timestamp_utc=_iso(fill_ts),
        fill_price=float(fill_price),
        fill_slippage_pct=fill_slippage_pct,
        fill_slippage_r=fill_slippage_r,
        invalidation_timestamp_utc="",
        invalidation_reason="",
        t1_timestamp_utc=_iso(t1_ts),
        exit_timestamp_utc=_iso(exit_ts),
        exit_price=float(exit_price),
        exit_reason=exit_reason,
        realized_r=realized_r,
        net_realized_r=net_realized_r,
        mae_pct=mae_pct,
        mfe_pct=mfe_pct,
        mae_r=mae_r,
        mfe_r=mfe_r,
        bars_to_trigger=bars_to_trigger,
        bars_to_fill=bars_to_fill,
        bars_to_exit=bars_to_exit,
        missed_opportunity_r=0.0,
        commission_cash=commission_cash,
        position_size=cfg.position_size,
        no_fill_reason="",
        audit_no_lookahead=audit_no_lookahead,
        audit_timestamps_strict=strict_ts,
        audit_deterministic=True,
        audit_notes=prep_note,
    )


def _missed_opportunity_r(
    future: pd.DataFrame,
    plan: dict,
    cfg: BacktestConfig,
    *,
    filled: bool,
) -> float:
    if filled:
        return 0.0
    if future.empty:
        return 0.0

    risk_reference = plan["max_acceptable_fill"] - plan["stop_price"]
    if risk_reference <= 0:
        return 0.0

    # A missed opportunity is counted only when T2 was subsequently reachable
    # inside the same deterministic horizon. This avoids assigning a speculative
    # positive R to every missed trigger.
    if float(future["high"].max()) < plan["t2_price"]:
        return 0.0

    return max(
        0.0,
        (plan["t2_price"] - plan["max_acceptable_fill"]) / risk_reference,
    )


def evaluate_signals(
    signals: pd.DataFrame,
    bars_by_symbol: dict[str, pd.DataFrame],
    *,
    config: BacktestConfig | None = None,
) -> pd.DataFrame:
    """Evaluate a signal table against symbol-specific OHLC bars."""
    if signals is None or signals.empty:
        return pd.DataFrame(columns=BACKTEST_OUTCOME_COLUMNS)

    cfg = config or BacktestConfig()
    rows: list[dict] = []

    for _, signal in signals.iterrows():
        symbol = _text(signal.get("symbol")).upper()
        if symbol not in bars_by_symbol:
            raise KeyError(f"No bars supplied for signal symbol {symbol}")
        outcome = evaluate_signal(signal, bars_by_symbol[symbol], config=cfg)
        rows.append(outcome.to_dict())

    return pd.DataFrame(rows, columns=BACKTEST_OUTCOME_COLUMNS)


def summarize_outcomes(outcomes: pd.DataFrame | None) -> dict:
    """Small audit summary; it does not claim statistical significance."""
    if outcomes is None or outcomes.empty:
        return {
            "signals": 0,
            "filled": 0,
            "no_fill": 0,
            "target2": 0,
            "stops": 0,
            "timeouts": 0,
            "mean_realized_r": None,
            "mean_net_realized_r": None,
            "mean_missed_opportunity_r": 0.0,
        }

    realized = pd.to_numeric(outcomes["realized_r"], errors="coerce")
    net = pd.to_numeric(outcomes["net_realized_r"], errors="coerce")
    missed = pd.to_numeric(outcomes["missed_opportunity_r"], errors="coerce").fillna(0.0)

    states = outcomes["outcome_state"].astype(str)
    return {
        "signals": int(len(outcomes)),
        "filled": int((outcomes["fill_status"].astype(str) == "FILLED").sum()),
        "no_fill": int((outcomes["fill_status"].astype(str) == "NO_FILL").sum()),
        "target2": int((states == "FILLED_TARGET2").sum()),
        "stops": int((states == "FILLED_STOP").sum()),
        "timeouts": int((states == "TIMEOUT").sum()),
        "mean_realized_r": None if realized.dropna().empty else float(realized.mean()),
        "mean_net_realized_r": None if net.dropna().empty else float(net.mean()),
        "mean_missed_opportunity_r": float(missed.mean()),
    }
