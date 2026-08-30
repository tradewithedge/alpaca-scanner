from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


FUNDAMENTALS_VERSION = "V1.2.2.1b"

SEC_TICKER_JSON_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_TICKER_TEXT_URL = "https://www.sec.gov/include/ticker.txt"
SEC_TICKER_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

# Streamlit Cloud has now been observed returning HTTP 403 for multiple
# www.sec.gov ticker/CIK association endpoints. To keep the financial source
# authoritative while bypassing that transport bottleneck, V1.2.2.1b permits
# one VERSION-PINNED SEC-derived identity mirror for ticker -> CIK resolution.
#
# IMPORTANT:
# - This mirror is used ONLY for identity metadata (ticker -> CIK).
# - Revenue / earnings / filing values are NEVER read from this mirror.
# - Financial facts still come only from official data.sec.gov CompanyFacts.
# - The URL is commit-pinned so content cannot silently change under the app.
SEC_IDENTITY_MIRROR_URL = (
    "https://raw.githubusercontent.com/"
    "louiscypher1993/stock-catalyst-historian/"
    "2b43f3d5136de5b2ee77dd5802855e2d525a94a6/"
    "src/scripts/cik_ticker_map.json"
)
SEC_IDENTITY_MIRROR_LABEL = "SEC-derived pinned GitHub identity mirror"

# SEC asks automated clients to identify themselves. A user-supplied
# SEC_USER_AGENT Streamlit secret is preferred. The default still identifies
# the project and provides a stable contact location without inventing an email.
DEFAULT_SEC_USER_AGENT = (
    "TradeWithEdge AlpacaScanner/1.2.2.1b "
    "(contact: https://github.com/tradewithedge/alpaca-scanner)"
)

SEC_RETRYABLE_STATUS = (429, 500, 502, 503, 504)

ALLOWED_FORMS = {
    "10-Q", "10-Q/A", "10-K", "10-K/A",
    "20-F", "20-F/A", "40-F", "40-F/A",
    "6-K", "6-K/A",
}

REVENUE_CONCEPTS = [
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "Revenues"),
    ("us-gaap", "SalesRevenueNet"),
    ("ifrs-full", "Revenue"),
]

EPS_CONCEPTS = [
    ("us-gaap", "EarningsPerShareDiluted"),
    ("us-gaap", "EarningsPerShareBasicAndDiluted"),
    ("ifrs-full", "DilutedEarningsLossPerShare"),
]

NET_INCOME_CONCEPTS = [
    ("us-gaap", "NetIncomeLoss"),
    ("ifrs-full", "ProfitLoss"),
]


class SecAccessError(RuntimeError):
    """Structured SEC transport/access failure used by the dashboard."""

    def __init__(
        self,
        message: str,
        *,
        stage: str,
        url: str,
        status_code: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.stage = stage
        self.url = url
        self.status_code = status_code
        self.retryable = retryable

    def compact(self) -> str:
        status = (
            f"HTTP {self.status_code}"
            if self.status_code is not None
            else "NETWORK/FORMAT"
        )
        return f"{self.stage}: {status} — {self}"


class SecIdentityNotFound(LookupError):
    pass


def normalize_sec_ticker(ticker: str) -> str:
    """Normalize common exchange punctuation to SEC ticker style."""
    return str(ticker or "").strip().upper().replace(".", "-")


def _headers(user_agent: str | None, *, accept: str) -> dict:
    ua = str(user_agent or DEFAULT_SEC_USER_AGENT).strip()
    return {
        "User-Agent": ua,
        "Accept-Encoding": "gzip, deflate",
        "Accept": accept,
        "Connection": "keep-alive",
    }


def _build_session(user_agent: str | None, *, accept: str) -> requests.Session:
    """Low-rate SEC session with bounded retry/backoff.

    403 is deliberately NOT retried. 429 and transient server failures are.
    """
    retry = Retry(
        total=3,
        connect=2,
        read=2,
        status=3,
        backoff_factor=0.8,
        status_forcelist=SEC_RETRYABLE_STATUS,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    session = requests.Session()
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=2,
        pool_maxsize=4,
    )
    session.mount("https://", adapter)
    session.headers.update(_headers(user_agent, accept=accept))
    return session


def _sec_get(
    url: str,
    *,
    stage: str,
    user_agent: str | None = None,
    timeout: float = 12.0,
    accept: str = "application/json,text/plain;q=0.9,*/*;q=0.8",
) -> requests.Response:
    session = _build_session(user_agent, accept=accept)
    try:
        response = session.get(
            url,
            timeout=(5.0, float(timeout)),
        )
    except requests.RequestException as exc:
        raise SecAccessError(
            str(exc),
            stage=stage,
            url=url,
            status_code=None,
            retryable=True,
        ) from exc
    finally:
        session.close()

    if response.status_code >= 400:
        retryable = response.status_code in SEC_RETRYABLE_STATUS
        snippet = (response.text or "").strip().replace("\n", " ")[:180]
        detail = (
            f"{response.reason or 'request failed'}"
            + (f" | {snippet}" if snippet else "")
        )
        raise SecAccessError(
            detail,
            stage=stage,
            url=url,
            status_code=int(response.status_code),
            retryable=retryable,
        )

    return response


def _parse_company_tickers_json(payload: dict) -> dict:
    out = {}
    for item in (payload or {}).values():
        ticker = normalize_sec_ticker(item.get("ticker"))
        cik = item.get("cik_str")
        if not ticker or cik is None:
            continue
        out[ticker] = {
            "ticker": ticker,
            "cik": int(cik),
            "title": str(item.get("title") or ""),
        }
    if not out:
        raise ValueError("SEC company_tickers.json returned no ticker/CIK rows.")
    return out


def _parse_ticker_txt(text: str) -> dict:
    out = {}
    for raw in str(text or "").splitlines():
        if "\t" not in raw:
            continue
        ticker_raw, cik_raw = raw.split("\t", 1)
        ticker = normalize_sec_ticker(ticker_raw)
        try:
            cik = int(str(cik_raw).strip())
        except Exception:
            continue
        if ticker:
            out[ticker] = {
                "ticker": ticker,
                "cik": cik,
                "title": "",
            }
    if not out:
        raise ValueError("SEC ticker.txt returned no ticker/CIK rows.")
    return out


def _parse_company_tickers_exchange(payload: dict) -> dict:
    fields = list((payload or {}).get("fields") or [])
    data = list((payload or {}).get("data") or [])
    if not fields or not data:
        raise ValueError(
            "SEC company_tickers_exchange.json returned no association rows."
        )

    try:
        cik_i = fields.index("cik")
        name_i = fields.index("name")
        ticker_i = fields.index("ticker")
    except ValueError as exc:
        raise ValueError(
            "SEC company_tickers_exchange.json schema is missing "
            "cik/name/ticker fields."
        ) from exc

    out = {}
    for row in data:
        try:
            ticker = normalize_sec_ticker(row[ticker_i])
            cik = int(row[cik_i])
            title = str(row[name_i] or "")
        except Exception:
            continue
        if ticker:
            out[ticker] = {
                "ticker": ticker,
                "cik": cik,
                "title": title,
            }

    if not out:
        raise ValueError(
            "SEC company_tickers_exchange.json produced no usable rows."
        )
    return out


def fetch_sec_ticker_map_json(
    user_agent: str | None = None,
    timeout: float = 12.0,
) -> dict:
    response = _sec_get(
        SEC_TICKER_JSON_URL,
        stage="SEC IDENTITY company_tickers.json",
        user_agent=user_agent,
        timeout=timeout,
        accept="application/json,*/*;q=0.8",
    )
    try:
        return _parse_company_tickers_json(response.json())
    except Exception as exc:
        raise SecAccessError(
            f"Invalid JSON/schema: {exc}",
            stage="SEC IDENTITY company_tickers.json",
            url=SEC_TICKER_JSON_URL,
        ) from exc


def fetch_sec_ticker_map_text(
    user_agent: str | None = None,
    timeout: float = 12.0,
) -> dict:
    response = _sec_get(
        SEC_TICKER_TEXT_URL,
        stage="SEC IDENTITY ticker.txt",
        user_agent=user_agent,
        timeout=timeout,
        accept="text/plain,*/*;q=0.8",
    )
    try:
        return _parse_ticker_txt(response.text)
    except Exception as exc:
        raise SecAccessError(
            f"Invalid ticker.txt payload: {exc}",
            stage="SEC IDENTITY ticker.txt",
            url=SEC_TICKER_TEXT_URL,
        ) from exc


def fetch_sec_ticker_map_exchange(
    user_agent: str | None = None,
    timeout: float = 12.0,
) -> dict:
    response = _sec_get(
        SEC_TICKER_EXCHANGE_URL,
        stage="SEC IDENTITY company_tickers_exchange.json",
        user_agent=user_agent,
        timeout=timeout,
        accept="application/json,*/*;q=0.8",
    )
    try:
        return _parse_company_tickers_exchange(response.json())
    except Exception as exc:
        raise SecAccessError(
            f"Invalid JSON/schema: {exc}",
            stage="SEC IDENTITY company_tickers_exchange.json",
            url=SEC_TICKER_EXCHANGE_URL,
        ) from exc



def _parse_sec_identity_mirror(payload: dict) -> dict:
    """Parse the commit-pinned CIK->ticker mirror into ticker->identity.

    The mirror contains identity metadata only. It is never accepted as a
    source of revenue, earnings, or any other financial fact.
    """
    out = {}
    if not isinstance(payload, dict):
        raise ValueError("SEC-derived identity mirror did not return an object.")

    for cik_raw, ticker_raw in payload.items():
        ticker = normalize_sec_ticker(ticker_raw)
        try:
            cik = int(str(cik_raw).strip())
        except Exception:
            continue
        if not ticker or cik <= 0:
            continue
        out[ticker] = {
            "ticker": ticker,
            "cik": cik,
            "title": "",
        }

    if not out:
        raise ValueError("SEC-derived identity mirror produced no usable rows.")
    return out


def fetch_sec_identity_mirror(
    timeout: float = 15.0,
) -> dict:
    """Fetch the version-pinned SEC-derived ticker/CIK transport mirror."""
    headers = {
        "User-Agent": "TradeWithEdge-AlpacaScanner/1.2.2.1b",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Encoding": "gzip, deflate",
    }
    try:
        response = requests.get(
            SEC_IDENTITY_MIRROR_URL,
            headers=headers,
            timeout=(5.0, float(timeout)),
        )
    except requests.RequestException as exc:
        raise SecAccessError(
            str(exc),
            stage="SEC IDENTITY MIRROR",
            url=SEC_IDENTITY_MIRROR_URL,
            retryable=True,
        ) from exc

    if response.status_code >= 400:
        raise SecAccessError(
            response.reason or "mirror request failed",
            stage="SEC IDENTITY MIRROR",
            url=SEC_IDENTITY_MIRROR_URL,
            status_code=int(response.status_code),
            retryable=response.status_code in SEC_RETRYABLE_STATUS,
        )

    try:
        return _parse_sec_identity_mirror(response.json())
    except Exception as exc:
        raise SecAccessError(
            f"Invalid identity-mirror payload: {exc}",
            stage="SEC IDENTITY MIRROR",
            url=SEC_IDENTITY_MIRROR_URL,
        ) from exc


def _identity_result(
    identity: dict,
    *,
    source_name: str,
    diagnostics: list[str],
    authority: str,
) -> dict:
    out = dict(identity)
    out.update(
        {
            "identity_source": source_name,
            "identity_authority": authority,
            "identity_access_status": "PASS",
            "identity_diagnostics": " | ".join(diagnostics),
        }
    )
    return out

def fetch_sec_ticker_map(
    user_agent: str | None = None,
    timeout: float = 12.0,
) -> dict:
    """Compatibility helper: fetch an official SEC ticker map with fallbacks."""
    errors = []
    for source_name, loader in (
        ("company_tickers.json", fetch_sec_ticker_map_json),
        ("ticker.txt", fetch_sec_ticker_map_text),
        ("company_tickers_exchange.json", fetch_sec_ticker_map_exchange),
    ):
        try:
            return loader(user_agent=user_agent, timeout=timeout)
        except SecAccessError as exc:
            errors.append(f"{source_name} [{exc.compact()}]")

    raise SecAccessError(
        "All official SEC ticker/CIK association sources failed: "
        + " | ".join(errors),
        stage="SEC IDENTITY ALL SOURCES",
        url=";".join(
            [
                SEC_TICKER_JSON_URL,
                SEC_TICKER_TEXT_URL,
                SEC_TICKER_EXCHANGE_URL,
            ]
        ),
    )


def resolve_sec_identity(
    ticker: str,
    user_agent: str | None = None,
    timeout: float = 12.0,
) -> dict:
    """Resolve ticker -> CIK with official-first, transport-bypass fallback.

    Normal path:
      official SEC association files -> official CompanyFacts.

    Streamlit Cloud transport-bypass path:
      version-pinned SEC-derived identity mirror -> official CompanyFacts.

    A 403 from www.sec.gov is treated as evidence that the host/path is
    blocked from the deployment environment. We do not waste additional
    requests probing every www.sec.gov identity file before trying the mirror.
    """
    ticker = normalize_sec_ticker(ticker)
    if not ticker:
        raise SecIdentityNotFound("Ticker is blank.")

    diagnostics: list[str] = []

    # 1) Primary official SEC identity endpoint.
    try:
        mapping = fetch_sec_ticker_map_json(
            user_agent=user_agent,
            timeout=timeout,
        )
        identity = mapping.get(ticker)
        if identity is not None:
            return _identity_result(
                identity,
                source_name="SEC company_tickers.json",
                diagnostics=diagnostics,
                authority="OFFICIAL SEC",
            )
        diagnostics.append(
            "SEC company_tickers.json: accessible, ticker not present"
        )
    except SecAccessError as exc:
        diagnostics.append(exc.compact())

        # We have live evidence that Streamlit Cloud can receive a host-level
        # 403 from www.sec.gov. In that case, immediately use the transport
        # mirror instead of repeating two more requests to the same blocked
        # host.
        if exc.status_code == 403:
            try:
                mirror = fetch_sec_identity_mirror(timeout=timeout)
                identity = mirror.get(ticker)
                if identity is not None:
                    return _identity_result(
                        identity,
                        source_name=SEC_IDENTITY_MIRROR_LABEL,
                        diagnostics=diagnostics,
                        authority="SEC-DERIVED MIRROR / FINANCIALS STILL OFFICIAL SEC",
                    )
                diagnostics.append(
                    f"{SEC_IDENTITY_MIRROR_LABEL}: accessible, ticker not present"
                )
            except SecAccessError as mirror_exc:
                diagnostics.append(mirror_exc.compact())

            raise SecAccessError(
                "www.sec.gov identity access returned HTTP 403 and the "
                "version-pinned SEC-derived mirror did not resolve the ticker. "
                + " | ".join(diagnostics),
                stage="SEC IDENTITY TRANSPORT BYPASS",
                url=SEC_IDENTITY_MIRROR_URL,
            )

    # 2) If the primary did not show host-level blocking, retain the other
    # official SEC association files before mirror fallback.
    for source_name, loader in (
        ("SEC ticker.txt", fetch_sec_ticker_map_text),
        ("SEC company_tickers_exchange.json", fetch_sec_ticker_map_exchange),
    ):
        try:
            mapping = loader(user_agent=user_agent, timeout=timeout)
        except SecAccessError as exc:
            diagnostics.append(exc.compact())
            continue

        identity = mapping.get(ticker)
        if identity is not None:
            return _identity_result(
                identity,
                source_name=source_name,
                diagnostics=diagnostics,
                authority="OFFICIAL SEC",
            )

        diagnostics.append(f"{source_name}: accessible, ticker not present")

    # 3) Transport-only mirror as final identity fallback.
    try:
        mirror = fetch_sec_identity_mirror(timeout=timeout)
        identity = mirror.get(ticker)
        if identity is not None:
            return _identity_result(
                identity,
                source_name=SEC_IDENTITY_MIRROR_LABEL,
                diagnostics=diagnostics,
                authority="SEC-DERIVED MIRROR / FINANCIALS STILL OFFICIAL SEC",
            )
        diagnostics.append(
            f"{SEC_IDENTITY_MIRROR_LABEL}: accessible, ticker not present"
        )
    except SecAccessError as exc:
        diagnostics.append(exc.compact())

    reachable_not_found = any(
        "accessible, ticker not present" in item for item in diagnostics
    )
    if reachable_not_found:
        raise SecIdentityNotFound(
            f"{ticker} was not found in the available SEC identity association "
            f"sources. Diagnostics: {' | '.join(diagnostics)}"
        )

    raise SecAccessError(
        "Unable to resolve ticker through official SEC identity endpoints or "
        "the version-pinned SEC-derived transport mirror. "
        + " | ".join(diagnostics),
        stage="SEC IDENTITY ALL ROUTES",
        url=";".join(
            [
                SEC_TICKER_JSON_URL,
                SEC_TICKER_TEXT_URL,
                SEC_TICKER_EXCHANGE_URL,
                SEC_IDENTITY_MIRROR_URL,
            ]
        ),
    )

def fetch_sec_companyfacts(
    cik: int,
    user_agent: str | None = None,
    timeout: float = 15.0,
) -> dict:
    """Fetch one issuer's official SEC CompanyFacts JSON."""
    url = SEC_COMPANYFACTS_URL.format(cik=int(cik))
    response = _sec_get(
        url,
        stage="SEC COMPANYFACTS",
        user_agent=user_agent,
        timeout=timeout,
        accept="application/json,*/*;q=0.8",
    )
    try:
        payload = response.json()
    except Exception as exc:
        raise SecAccessError(
            f"Invalid CompanyFacts JSON: {exc}",
            stage="SEC COMPANYFACTS",
            url=url,
        ) from exc

    if not isinstance(payload, dict) or not payload.get("facts"):
        raise SecAccessError(
            "CompanyFacts response did not contain a usable 'facts' object.",
            stage="SEC COMPANYFACTS",
            url=url,
        )

    # Guard against a bad/stale mirror identity. The requested CIK and the
    # official CompanyFacts CIK must agree whenever the API exposes it.
    payload_cik = payload.get("cik")
    if payload_cik is not None:
        try:
            payload_cik = int(payload_cik)
        except Exception:
            raise SecAccessError(
                "CompanyFacts returned a non-numeric CIK.",
                stage="SEC COMPANYFACTS IDENTITY VALIDATION",
                url=url,
            )
        if payload_cik != int(cik):
            raise SecAccessError(
                f"CompanyFacts CIK mismatch: requested {int(cik)}, "
                f"received {payload_cik}.",
                stage="SEC COMPANYFACTS IDENTITY VALIDATION",
                url=url,
            )

    return payload

def _to_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def _numeric(value):
    try:
        value = float(value)
    except Exception:
        return np.nan
    return value if np.isfinite(value) else np.nan


def _unit_priority(unit: str, metric_kind: str) -> int:
    u = str(unit or "")
    ul = u.lower()

    if metric_kind == "eps":
        if "shares" not in ul:
            return 999
        if u == "USD/shares":
            return 0
        return 10

    # Revenue / net income: currency values only, never shares or per-share.
    if "shares" in ul or "/" in u:
        return 999
    if u == "USD":
        return 0
    if len(u) == 3 and u.isalpha():
        return 10
    return 100


def _concept_observations(
    companyfacts: dict,
    taxonomy: str,
    concept: str,
    metric_kind: str,
) -> tuple[pd.DataFrame, str | None]:
    fact = (
        companyfacts.get("facts", {})
        .get(taxonomy, {})
        .get(concept)
    )
    if not fact:
        return pd.DataFrame(), None

    units = fact.get("units", {}) or {}
    ranked = sorted(
        (
            (_unit_priority(unit, metric_kind), unit, items)
            for unit, items in units.items()
        ),
        key=lambda x: x[0],
    )
    ranked = [x for x in ranked if x[0] < 999]
    if not ranked:
        return pd.DataFrame(), None

    _, selected_unit, items = ranked[0]
    rows = []
    for item in items:
        if item.get("form") not in ALLOWED_FORMS:
            continue
        start = _to_date(item.get("start"))
        end = _to_date(item.get("end"))
        filed = _to_date(item.get("filed"))
        val = _numeric(item.get("val"))
        if start is None or end is None or pd.isna(val):
            continue
        duration_days = (end - start).days
        if duration_days <= 0:
            continue
        rows.append(
            {
                "start": start,
                "end": end,
                "filed": filed,
                "val": float(val),
                "form": item.get("form"),
                "fy": item.get("fy"),
                "fp": item.get("fp"),
                "accn": item.get("accn"),
                "duration_days": duration_days,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df, selected_unit

    # Restatements/amendments may repeat a period. Prefer the most recently
    # filed value for an identical start/end period.
    df["_filed_sort"] = pd.to_datetime(df["filed"], errors="coerce")
    df = (
        df.sort_values(["start", "end", "_filed_sort"])
        .drop_duplicates(["start", "end"], keep="last")
        .drop(columns="_filed_sort")
        .reset_index(drop=True)
    )
    return df, selected_unit


def _choose_concept(
    companyfacts: dict,
    candidates: Iterable[tuple[str, str]],
    metric_kind: str,
) -> dict:
    """Choose the first declared taxonomy concept with usable observations."""
    for taxonomy, concept in candidates:
        df, unit = _concept_observations(
            companyfacts,
            taxonomy,
            concept,
            metric_kind,
        )
        if not df.empty:
            return {
                "taxonomy": taxonomy,
                "concept": concept,
                "unit": unit,
                "observations": df,
            }
    return {
        "taxonomy": None,
        "concept": None,
        "unit": None,
        "observations": pd.DataFrame(),
    }


def _period_series(observations: pd.DataFrame, period: str) -> pd.DataFrame:
    if observations is None or observations.empty:
        return pd.DataFrame()

    df = observations.copy()
    if period == "quarter":
        df = df[(df["duration_days"] >= 60) & (df["duration_days"] <= 120)]
    elif period == "annual":
        df = df[(df["duration_days"] >= 300) & (df["duration_days"] <= 430)]
    else:
        raise ValueError("period must be 'quarter' or 'annual'")

    if df.empty:
        return df

    # Multiple facts can share the same end date with slightly different start
    # dates. Choose the duration closest to a standard reporting period.
    target = 91 if period == "quarter" else 365
    df["_duration_gap"] = (df["duration_days"] - target).abs()
    df["_filed_sort"] = pd.to_datetime(df["filed"], errors="coerce")
    df = (
        df.sort_values(["end", "_duration_gap", "_filed_sort"])
        .drop_duplicates(["end"], keep="first")
        .drop(columns=["_duration_gap", "_filed_sort"])
        .sort_values("end")
        .reset_index(drop=True)
    )
    return df


def _find_yoy_prior(df: pd.DataFrame, index: int):
    if df is None or df.empty or index < 0 or index >= len(df):
        return None
    current_end = df.iloc[index]["end"]
    candidates = []
    for j in range(index):
        delta = (current_end - df.iloc[j]["end"]).days
        if 320 <= delta <= 410:
            candidates.append((abs(delta - 365), j))
    if not candidates:
        return None
    _, j = min(candidates, key=lambda x: x[0])
    return df.iloc[j]


def _growth(current: float, prior: float, earnings: bool = False):
    if not np.isfinite(current) or not np.isfinite(prior):
        return np.nan, "N/A"

    if earnings:
        if prior <= 0 < current:
            return np.nan, "TURNAROUND"
        if current <= 0 < prior:
            return np.nan, "PROFIT TO LOSS"
        if current <= 0 and prior <= 0:
            return np.nan, "LOSS"
        if prior <= 0:
            return np.nan, "N/M"

    if prior == 0:
        return np.nan, "N/M"

    return float(current / prior - 1.0), "GROWTH"


def _yoy_observations(
    series: pd.DataFrame,
    *,
    earnings: bool,
) -> list[dict]:
    out = []
    if series is None or series.empty:
        return out

    for i in range(len(series)):
        prior = _find_yoy_prior(series, i)
        if prior is None:
            continue
        current = series.iloc[i]
        growth, state = _growth(
            float(current["val"]),
            float(prior["val"]),
            earnings=earnings,
        )
        out.append(
            {
                "end": current["end"],
                "filed": current["filed"],
                "current": float(current["val"]),
                "prior": float(prior["val"]),
                "growth": growth,
                "state": state,
            }
        )
    return out


def _latest_growth(series: pd.DataFrame, earnings: bool = False) -> dict:
    obs = _yoy_observations(series, earnings=earnings)
    if not obs:
        return {
            "growth": np.nan,
            "state": "N/A",
            "end": None,
            "filed": None,
            "prior_growth": np.nan,
            "change": np.nan,
            "positive_count": 0,
            "valid_count": 0,
        }

    latest = obs[-1]
    previous_valid = next(
        (
            item for item in reversed(obs[:-1])
            if np.isfinite(item.get("growth", np.nan))
        ),
        None,
    )

    prior_growth = (
        float(previous_valid["growth"])
        if previous_valid is not None
        else np.nan
    )
    latest_growth = latest.get("growth", np.nan)
    change = (
        float(latest_growth - prior_growth)
        if np.isfinite(latest_growth) and np.isfinite(prior_growth)
        else np.nan
    )

    recent = obs[-4:]
    valid_growths = [
        item["growth"]
        for item in recent
        if np.isfinite(item.get("growth", np.nan))
    ]

    return {
        "growth": latest_growth,
        "state": latest.get("state", "N/A"),
        "end": latest.get("end"),
        "filed": latest.get("filed"),
        "prior_growth": prior_growth,
        "change": change,
        "positive_count": int(sum(g > 0 for g in valid_growths)),
        "valid_count": int(len(valid_growths)),
    }


def _latest_annual_growth(series: pd.DataFrame, earnings: bool = False) -> dict:
    if series is None or len(series) < 2:
        return {"growth": np.nan, "state": "N/A", "end": None, "filed": None}

    current = series.iloc[-1]
    prior = series.iloc[-2]
    growth, state = _growth(
        float(current["val"]),
        float(prior["val"]),
        earnings=earnings,
    )
    return {
        "growth": growth,
        "state": state,
        "end": current["end"],
        "filed": current["filed"],
    }


def _interp_score(value, points) -> float:
    if value is None or not np.isfinite(value):
        return np.nan
    xs = np.array([p[0] for p in points], dtype=float)
    ys = np.array([p[1] for p in points], dtype=float)
    return float(np.interp(float(value), xs, ys))


def _growth_component(value, earnings=False) -> float:
    if earnings:
        points = [
            (-0.50, 0), (-0.20, 10), (0.00, 35), (0.10, 55),
            (0.20, 68), (0.40, 82), (0.70, 95), (1.00, 100),
        ]
    else:
        points = [
            (-0.20, 0), (-0.10, 10), (0.00, 35), (0.05, 50),
            (0.10, 62), (0.20, 78), (0.30, 88), (0.50, 100),
        ]
    return _interp_score(value, points)


def _earnings_state_score(state: str) -> float:
    return {
        "TURNAROUND": 72.0,
        "PROFIT TO LOSS": 0.0,
        "LOSS": 10.0,
        "N/M": 25.0,
        "N/A": np.nan,
    }.get(str(state or "N/A"), np.nan)


def _momentum_score(change) -> float:
    return _interp_score(
        change,
        [
            (-0.30, 0), (-0.15, 15), (-0.05, 35), (0.00, 50),
            (0.05, 65), (0.10, 78), (0.20, 92), (0.30, 100),
        ],
    )


def _consistency_score(positive_count: int, valid_count: int) -> float:
    if not valid_count:
        return np.nan
    return 100.0 * float(positive_count) / float(valid_count)


def _grade(score) -> str:
    if score is None or pd.isna(score):
        return "N/A"
    score = float(score)
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def _fmt_pct(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}%"


def _fmt_pp(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}pp"


def build_fundamental_snapshot(
    ticker: str,
    companyfacts: dict,
    *,
    cik: int | None = None,
    company_name: str | None = None,
    as_of: date | None = None,
) -> dict:
    """Build explainable revenue/earnings diagnostics from SEC CompanyFacts.

    V1.2.2.1a remains deliberately SHADOW MODE. This function does not know about or
    modify scanner eligibility, buckets, entry quality, or trade decisions.
    """
    ticker = normalize_sec_ticker(ticker)
    as_of = as_of or date.today()

    revenue = _choose_concept(companyfacts, REVENUE_CONCEPTS, "revenue")
    eps = _choose_concept(companyfacts, EPS_CONCEPTS, "eps")
    net_income = _choose_concept(
        companyfacts,
        NET_INCOME_CONCEPTS,
        "net_income",
    )

    earnings_source = eps if not eps["observations"].empty else net_income
    earnings_metric = (
        "Diluted EPS"
        if earnings_source is eps and not eps["observations"].empty
        else "Net Income"
        if not net_income["observations"].empty
        else "Unavailable"
    )

    rev_q = _period_series(revenue["observations"], "quarter")
    rev_a = _period_series(revenue["observations"], "annual")
    earn_q = _period_series(earnings_source["observations"], "quarter")
    earn_a = _period_series(earnings_source["observations"], "annual")

    rev_q_growth = _latest_growth(rev_q, earnings=False)
    earn_q_growth = _latest_growth(earn_q, earnings=True)
    rev_a_growth = _latest_annual_growth(rev_a, earnings=False)
    earn_a_growth = _latest_annual_growth(earn_a, earnings=True)

    components = {
        "quarter_revenue": (
            _growth_component(rev_q_growth["growth"], earnings=False),
            25.0,
        ),
        "quarter_earnings": (
            _growth_component(earn_q_growth["growth"], earnings=True)
            if np.isfinite(earn_q_growth["growth"])
            else _earnings_state_score(earn_q_growth["state"]),
            25.0,
        ),
        "annual_revenue": (
            _growth_component(rev_a_growth["growth"], earnings=False),
            10.0,
        ),
        "annual_earnings": (
            _growth_component(earn_a_growth["growth"], earnings=True)
            if np.isfinite(earn_a_growth["growth"])
            else _earnings_state_score(earn_a_growth["state"]),
            10.0,
        ),
        "revenue_consistency": (
            _consistency_score(
                rev_q_growth["positive_count"],
                rev_q_growth["valid_count"],
            ),
            10.0,
        ),
        "earnings_consistency": (
            _consistency_score(
                earn_q_growth["positive_count"],
                earn_q_growth["valid_count"],
            ),
            10.0,
        ),
        "revenue_acceleration": (
            _momentum_score(rev_q_growth["change"]),
            5.0,
        ),
        "earnings_acceleration": (
            _momentum_score(earn_q_growth["change"]),
            5.0,
        ),
    }

    weighted_sum = 0.0
    available_weight = 0.0
    for value, weight in components.values():
        if value is not None and np.isfinite(value):
            weighted_sum += float(value) * weight
            available_weight += weight

    score = (
        weighted_sum / available_weight
        if available_weight >= 60.0
        else np.nan
    )

    latest_filed_candidates = [
        rev_q_growth.get("filed"),
        earn_q_growth.get("filed"),
        rev_a_growth.get("filed"),
        earn_a_growth.get("filed"),
    ]
    latest_filed_candidates = [
        d for d in latest_filed_candidates if isinstance(d, date)
    ]
    latest_filed = max(latest_filed_candidates) if latest_filed_candidates else None
    age_days = (as_of - latest_filed).days if latest_filed else None

    rev_has_q = rev_q_growth["end"] is not None
    earn_has_q = earn_q_growth["end"] is not None
    both_growth_domains = (
        revenue["concept"] is not None
        and earnings_source["concept"] is not None
    )

    if not both_growth_domains:
        confidence = "UNKNOWN"
    elif (
        rev_has_q
        and earn_has_q
        and age_days is not None
        and age_days <= 180
        and available_weight >= 80
        and earnings_metric == "Diluted EPS"
    ):
        confidence = "HIGH"
    elif (
        age_days is not None
        and age_days <= 270
        and available_weight >= 60
    ):
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    reasons = []
    risks = []

    rg = rev_q_growth["growth"]
    eg = earn_q_growth["growth"]

    if np.isfinite(rg):
        if rg >= 0.20:
            reasons.append(f"quarterly revenue growth {_fmt_pct(rg)}")
        elif rg < 0:
            risks.append(f"quarterly revenue growth {_fmt_pct(rg)}")
        else:
            reasons.append(f"quarterly revenue growth {_fmt_pct(rg)}")
    else:
        risks.append("quarterly revenue YoY unavailable")

    if np.isfinite(eg):
        if eg >= 0.20:
            reasons.append(
                f"quarterly {earnings_metric.lower()} growth {_fmt_pct(eg)}"
            )
        elif eg < 0:
            risks.append(
                f"quarterly {earnings_metric.lower()} growth {_fmt_pct(eg)}"
            )
        else:
            reasons.append(
                f"quarterly {earnings_metric.lower()} growth {_fmt_pct(eg)}"
            )
    elif earn_q_growth["state"] == "TURNAROUND":
        reasons.append(f"{earnings_metric} turned positive year-over-year")
    elif earn_q_growth["state"] not in {"N/A", "GROWTH"}:
        risks.append(
            f"{earnings_metric} state: {earn_q_growth['state']}"
        )
    else:
        risks.append(f"quarterly {earnings_metric.lower()} YoY unavailable")

    for label, change in [
        ("revenue", rev_q_growth["change"]),
        ("earnings", earn_q_growth["change"]),
    ]:
        if np.isfinite(change):
            phrase = (
                f"{label} growth momentum "
                f"{_fmt_pct(rev_q_growth['prior_growth'] if label == 'revenue' else earn_q_growth['prior_growth'])}"
                f" → {_fmt_pct(rg if label == 'revenue' else eg)} "
                f"({_fmt_pp(change)})"
            )
            if change >= 0.05:
                reasons.append("accelerating " + phrase)
            elif change <= -0.05:
                risks.append("decelerating " + phrase)

    if confidence != "HIGH":
        risks.append(f"Fundamental Data Confidence {confidence}")

    return {
        "ticker": ticker,
        "cik": cik,
        "company_name": company_name or companyfacts.get("entityName") or "",
        "source": "SEC EDGAR CompanyFacts",
        "fundamental_version": FUNDAMENTALS_VERSION,
        "sec_access_status": "PASS",
        "identity_access_status": "PASS",
        "companyfacts_access_status": "PASS",
        "identity_source": None,
        "identity_authority": None,
        "identity_diagnostics": "",
        "access_detail": "",
        "fundamental_score": round(float(score), 1) if np.isfinite(score) else np.nan,
        "fundamental_grade": _grade(score),
        "fundamental_confidence": confidence,
        "available_weight_pct": round(float(available_weight), 1),
        "latest_filed": latest_filed,
        "latest_filed_age_days": age_days,
        "revenue_taxonomy": revenue["taxonomy"],
        "revenue_concept": revenue["concept"],
        "revenue_unit": revenue["unit"],
        "earnings_taxonomy": earnings_source["taxonomy"],
        "earnings_concept": earnings_source["concept"],
        "earnings_unit": earnings_source["unit"],
        "earnings_metric": earnings_metric,
        "revenue_q_yoy": rev_q_growth["growth"],
        "revenue_q_end": rev_q_growth["end"],
        "revenue_q_prior_yoy": rev_q_growth["prior_growth"],
        "revenue_q_change": rev_q_growth["change"],
        "revenue_positive_count": rev_q_growth["positive_count"],
        "revenue_valid_count": rev_q_growth["valid_count"],
        "earnings_q_yoy": earn_q_growth["growth"],
        "earnings_q_state": earn_q_growth["state"],
        "earnings_q_end": earn_q_growth["end"],
        "earnings_q_prior_yoy": earn_q_growth["prior_growth"],
        "earnings_q_change": earn_q_growth["change"],
        "earnings_positive_count": earn_q_growth["positive_count"],
        "earnings_valid_count": earn_q_growth["valid_count"],
        "revenue_annual_yoy": rev_a_growth["growth"],
        "revenue_annual_state": rev_a_growth["state"],
        "revenue_annual_end": rev_a_growth["end"],
        "earnings_annual_yoy": earn_a_growth["growth"],
        "earnings_annual_state": earn_a_growth["state"],
        "earnings_annual_end": earn_a_growth["end"],
        "fundamental_reasons": "; ".join(reasons),
        "fundamental_risks": "; ".join(risks),
    }


def unavailable_snapshot(
    ticker: str,
    reason: str,
    *,
    cik: int | None = None,
    company_name: str | None = None,
    sec_access_status: str = "FAILED",
    identity_access_status: str = "UNKNOWN",
    companyfacts_access_status: str = "UNKNOWN",
    identity_source: str | None = None,
    identity_authority: str | None = None,
    identity_diagnostics: str = "",
) -> dict:
    """Explicit fail-safe object. Never manufactures a fundamental score."""
    return {
        "ticker": normalize_sec_ticker(ticker),
        "cik": cik,
        "company_name": company_name or "",
        "source": "SEC EDGAR CompanyFacts",
        "fundamental_version": FUNDAMENTALS_VERSION,
        "sec_access_status": sec_access_status,
        "identity_access_status": identity_access_status,
        "companyfacts_access_status": companyfacts_access_status,
        "identity_source": identity_source,
        "identity_authority": identity_authority,
        "identity_diagnostics": identity_diagnostics,
        "access_detail": str(reason),
        "fundamental_score": np.nan,
        "fundamental_grade": "N/A",
        "fundamental_confidence": "UNKNOWN",
        "available_weight_pct": 0.0,
        "latest_filed": None,
        "latest_filed_age_days": None,
        "revenue_q_yoy": np.nan,
        "revenue_q_prior_yoy": np.nan,
        "revenue_q_change": np.nan,
        "revenue_positive_count": 0,
        "revenue_valid_count": 0,
        "earnings_q_yoy": np.nan,
        "earnings_q_prior_yoy": np.nan,
        "earnings_q_change": np.nan,
        "earnings_positive_count": 0,
        "earnings_valid_count": 0,
        "earnings_metric": "Unavailable",
        "earnings_q_state": "N/A",
        "revenue_annual_yoy": np.nan,
        "earnings_annual_yoy": np.nan,
        "fundamental_reasons": "",
        "fundamental_risks": str(reason),
    }
