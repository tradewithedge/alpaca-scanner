from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Iterable, Mapping

import pandas as pd


REPLAY_BAR_COLUMNS = ["timestamp", "open", "high", "low", "close"]


class ReplayIntegrityError(ValueError):
    """Raised when historical replay inputs are ambiguous or violate as-of rules."""


@dataclass(frozen=True)
class ReplaySlice:
    symbol: str
    signal_timestamp_utc: pd.Timestamp
    asof_bars: pd.DataFrame
    future_bars: pd.DataFrame
    latest_asof_timestamp_utc: pd.Timestamp | None
    asof_row_count: int
    future_row_count: int
    source_fingerprint: str


@dataclass(frozen=True)
class ReplayEvaluation:
    symbol: str
    signal_timestamp_utc: str
    source_fingerprint: str
    result: object



def _utc_timestamp(value) -> pd.Timestamp:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        raise ReplayIntegrityError(f"invalid UTC timestamp: {value!r}")
    return ts


def _normalise_symbol(value: object) -> str:
    symbol = str(value or "").upper().strip()
    if not symbol:
        raise ReplayIntegrityError("symbol is required")
    return symbol


def _canonicalise_bars(bars: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if bars is None or bars.empty:
        raise ReplayIntegrityError(f"no historical bars supplied for {symbol}")

    frame = bars.copy(deep=True)
    if "symbol" in frame.columns:
        frame = frame[frame["symbol"].astype(str).str.upper().str.strip() == symbol].copy()
    elif "Symbol" in frame.columns:
        frame = frame[frame["Symbol"].astype(str).str.upper().str.strip() == symbol].copy()
    else:
        raise ReplayIntegrityError("historical bars must include a symbol column")

    rename_map = {}
    if "datetime" in frame.columns and "timestamp" not in frame.columns:
        rename_map["datetime"] = "timestamp"
    if "date" in frame.columns and "timestamp" not in frame.columns:
        rename_map["date"] = "timestamp"
    frame = frame.rename(columns=rename_map)

    missing = [c for c in REPLAY_BAR_COLUMNS if c not in frame.columns]
    if missing:
        raise ReplayIntegrityError(f"missing bar columns for {symbol}: {missing}")

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    if frame["timestamp"].isna().any():
        raise ReplayIntegrityError(f"invalid bar timestamp detected for {symbol}")

    if frame["timestamp"].duplicated().any():
        duplicates = frame.loc[frame["timestamp"].duplicated(keep=False), "timestamp"].astype(str).tolist()
        raise ReplayIntegrityError(f"duplicate timestamps for {symbol}: {duplicates[:3]}")

    for column in ["open", "high", "low", "close"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ReplayIntegrityError(f"non-numeric OHLC values detected for {symbol} column={column}")

    frame = frame.sort_values("timestamp").reset_index(drop=True)
    return frame


def _fingerprint(frame: pd.DataFrame) -> str:
    canonical = frame[REPLAY_BAR_COLUMNS].copy()
    canonical["timestamp"] = canonical["timestamp"].astype(str)
    payload = canonical.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return "sha256:" + sha256(payload).hexdigest()


def build_replay_slice(
    *,
    symbol: str,
    signal_timestamp_utc,
    bars: pd.DataFrame,
    lookback_bars: int | None = None,
) -> ReplaySlice:
    """Create a strict as-of replay slice.

    ``asof_bars`` contains bars at or before the signal timestamp. ``future_bars``
    contains bars strictly after it. No future row is exposed to the signal-time
    evaluator. The signal bar is therefore available for planning/reference while
    future bars remain isolated for outcome evaluation.
    """
    symbol_n = _normalise_symbol(symbol)
    signal_ts = _utc_timestamp(signal_timestamp_utc)
    frame = _canonicalise_bars(bars, symbol_n)

    asof = frame.loc[frame["timestamp"] <= signal_ts].copy()
    future = frame.loc[frame["timestamp"] > signal_ts].copy()

    if asof.empty:
        raise ReplayIntegrityError(
            f"no as-of bar exists at or before signal timestamp for {symbol_n}: {signal_ts.isoformat()}"
        )

    if lookback_bars is not None:
        if int(lookback_bars) <= 0:
            raise ReplayIntegrityError("lookback_bars must be > 0 when supplied")
        asof = asof.tail(int(lookback_bars)).reset_index(drop=True)

    leaked = asof.loc[asof["timestamp"] > signal_ts]
    if not leaked.empty:
        raise ReplayIntegrityError("future bar leaked into as-of slice")

    return ReplaySlice(
        symbol=symbol_n,
        signal_timestamp_utc=signal_ts,
        asof_bars=asof,
        future_bars=future.reset_index(drop=True),
        latest_asof_timestamp_utc=asof["timestamp"].max(),
        asof_row_count=int(len(asof)),
        future_row_count=int(len(future)),
        source_fingerprint=_fingerprint(frame),
    )


def replay_signal(
    *,
    symbol: str,
    signal_timestamp_utc,
    bars: pd.DataFrame,
    evaluator: Callable[[pd.DataFrame, pd.DataFrame, pd.Timestamp], object],
    lookback_bars: int | None = None,
) -> ReplayEvaluation:
    """Run a caller-supplied signal-time evaluator with future data isolated."""
    replay = build_replay_slice(
        symbol=symbol,
        signal_timestamp_utc=signal_timestamp_utc,
        bars=bars,
        lookback_bars=lookback_bars,
    )
    result = evaluator(
        replay.asof_bars.copy(deep=True),
        replay.future_bars.copy(deep=True),
        replay.signal_timestamp_utc,
    )
    return ReplayEvaluation(
        symbol=replay.symbol,
        signal_timestamp_utc=replay.signal_timestamp_utc.isoformat(),
        source_fingerprint=replay.source_fingerprint,
        result=result,
    )


def replay_signals(
    signals: Iterable[Mapping[str, object]] | pd.DataFrame,
    bars_by_symbol: Mapping[str, pd.DataFrame],
    evaluator: Callable[[pd.DataFrame, pd.DataFrame, pd.Timestamp], object],
    *,
    lookback_bars: int | None = None,
) -> list[ReplayEvaluation]:
    """Replay multiple historical signal-time states deterministically."""
    frame = signals.copy(deep=True) if isinstance(signals, pd.DataFrame) else pd.DataFrame(list(signals))
    if frame.empty:
        return []
    required = {"symbol", "signal_timestamp_utc"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ReplayIntegrityError(f"signal dataset missing columns: {missing}")

    outputs: list[ReplayEvaluation] = []
    for _, row in frame.iterrows():
        symbol = _normalise_symbol(row["symbol"])
        matching_key = next((key for key in bars_by_symbol if str(key).upper().strip() == symbol), None)
        if matching_key is None:
            raise ReplayIntegrityError(f"bars not found for signal symbol: {symbol}")
        outputs.append(
            replay_signal(
                symbol=symbol,
                signal_timestamp_utc=row["signal_timestamp_utc"],
                bars=bars_by_symbol[matching_key],
                evaluator=evaluator,
                lookback_bars=lookback_bars,
            )
        )
    return outputs


__all__ = [
    "REPLAY_BAR_COLUMNS",
    "ReplayEvaluation",
    "ReplayIntegrityError",
    "ReplaySlice",
    "build_replay_slice",
    "replay_signal",
    "replay_signals",
]
