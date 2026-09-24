from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Iterable

import pandas as pd

from scanner.v17_signal_dataset_adapter import (
    ADAPTER_OUTPUT_COLUMNS,
    OUTCOME_COLUMNS,
    V13F_REQUIRED_COLUMNS,
    _fingerprint_row,
    normalize_v13f_capture,
)


# Signal-time fields must remain immutable once a capture_id is accepted.
# Outcome fields may legitimately transition from UNRECORDED to genuine recorded evidence.
SIGNAL_IMMUTABLE_COLUMNS = [
    c for c in V13F_REQUIRED_COLUMNS if c not in OUTCOME_COLUMNS
]

INTAKE_OUTPUT_COLUMNS = [
    "capture_id",
    "signal_key",
    "intake_state",
    "source_row_fingerprint",
    "prior_source_row_fingerprint",
    "outcome_state_normalized",
    "outcome_recorded",
    "notes",
]


def _load(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy(deep=True)
    return pd.read_csv(Path(source))


def _signal_fingerprint(row: pd.Series) -> str:
    payload = "|".join(f"{c}={row.get(c)!s}" for c in SIGNAL_IMMUTABLE_COLUMNS)
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def _index_by_capture(frame: pd.DataFrame) -> dict[str, pd.Series]:
    return {str(row["capture_id"]): row for _, row in frame.iterrows()}


def audit_cumulative_capture_delta(
    current_source: str | Path | pd.DataFrame,
    prior_source: str | Path | pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Audit a cumulative V1.3f export against a prior accepted capture set.

    Returns (accepted_updated_dataset, intake_audit, report).

    Rules:
    - New capture_ids are NEW_SIGNAL records.
    - Existing capture_ids with unchanged signal-time fields are UNCHANGED or
      OUTCOME_UPDATE when genuine outcome fields changed.
    - Existing capture_ids with changed signal-time fields are SIGNAL_MUTATION
      and are blocked from the accepted dataset.
    - No outcome is inferred from market prices.
    """
    current = normalize_v13f_capture(_load(current_source))
    prior = (
        normalize_v13f_capture(_load(prior_source))
        if prior_source is not None
        else pd.DataFrame(columns=ADAPTER_OUTPUT_COLUMNS)
    )

    prior_map = _index_by_capture(prior) if not prior.empty else {}
    accepted_rows: list[pd.Series] = []
    audit_rows: list[dict] = []
    blocked = 0
    new_signals = 0
    unchanged = 0
    outcome_updates = 0

    for _, row in current.iterrows():
        cid = str(row["capture_id"])
        current_signal_fp = _signal_fingerprint(row)
        prior_row = prior_map.get(cid)

        if prior_row is None:
            intake_state = "NEW_SIGNAL"
            note = "New capture_id in cumulative export."
            accepted_rows.append(row)
            new_signals += 1
            prior_fp = ""
        else:
            prior_signal_fp = _signal_fingerprint(prior_row)
            prior_fp = str(prior_row.get("source_row_fingerprint", ""))
            if current_signal_fp != prior_signal_fp:
                intake_state = "SIGNAL_MUTATION"
                note = "Blocked: signal-time fields changed for an accepted capture_id."
                blocked += 1
                accepted_rows.append(prior_row)
            else:
                prior_outcome = str(prior_row.get("outcome_state_normalized", "UNRECORDED"))
                current_outcome = str(row.get("outcome_state_normalized", "UNRECORDED"))
                outcome_changed = (
                    current_outcome != prior_outcome
                    or str(row.get("fill_status", "")) != str(prior_row.get("fill_status", ""))
                    or str(row.get("realized_r", "")) != str(prior_row.get("realized_r", ""))
                    or str(row.get("exit_price", "")) != str(prior_row.get("exit_price", ""))
                )
                if outcome_changed and current_outcome != "UNRECORDED":
                    intake_state = "OUTCOME_UPDATE"
                    note = "Signal-time fields unchanged; explicit outcome evidence updated."
                    accepted_rows.append(row)
                    outcome_updates += 1
                else:
                    intake_state = "UNCHANGED"
                    note = "Existing accepted signal unchanged; no new outcome evidence."
                    accepted_rows.append(prior_row)
                    unchanged += 1

        audit_rows.append(
            {
                "capture_id": cid,
                "signal_key": row.get("signal_key", ""),
                "intake_state": intake_state,
                "source_row_fingerprint": row.get("source_row_fingerprint", ""),
                "prior_source_row_fingerprint": prior_fp,
                "outcome_state_normalized": row.get("outcome_state_normalized", "UNRECORDED"),
                "outcome_recorded": bool(row.get("outcome_recorded", False)),
                "notes": note,
            }
        )

    accepted = pd.DataFrame(accepted_rows).reindex(columns=ADAPTER_OUTPUT_COLUMNS)
    if not accepted.empty:
        accepted = accepted.sort_values(["signal_timestamp_parsed", "symbol"]).reset_index(drop=True)

    audit = pd.DataFrame(audit_rows, columns=INTAKE_OUTPUT_COLUMNS)
    report = {
        "current_rows": int(len(current)),
        "prior_rows": int(len(prior)),
        "accepted_rows": int(len(accepted)),
        "new_signals": int(new_signals),
        "outcome_updates": int(outcome_updates),
        "unchanged": int(unchanged),
        "signal_mutations_blocked": int(blocked),
        "audit_pass": bool(blocked == 0 and audit["capture_id"].is_unique and audit["signal_key"].is_unique),
        "note": "Cumulative-export delta audit only; no outcome inference from prices.",
    }
    return accepted, audit, report


def audit_capture_history(
    sources: Iterable[str | Path | pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sequentially audit multiple cumulative exports in chronological order."""
    accepted = pd.DataFrame(columns=ADAPTER_OUTPUT_COLUMNS)
    reports: list[dict] = []
    for source in sources:
        accepted, _, report = audit_cumulative_capture_delta(source, accepted)
        reports.append(report)
    return accepted, pd.DataFrame(reports)


__all__ = [
    "INTAKE_OUTPUT_COLUMNS",
    "SIGNAL_IMMUTABLE_COLUMNS",
    "audit_capture_history",
    "audit_cumulative_capture_delta",
]
