import importlib
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Streamlit multi-file hot-reload guard.
# Reload the scanner package modules in dependency order so a GitHub deploy
# cannot leave app.py running against stale dataclasses / scoring functions.
# -----------------------------------------------------------------------------
import scanner.alpaca_client as alpaca_client_module
import scanner.audit as audit_module
import scanner.config as scanner_config
import scanner.indicators as indicators_module
import scanner.inspector as inspector_module
import scanner.fundamentals as fundamentals_module
import scanner.leadership as leadership_module
import scanner.regime as regime_module
import scanner.scoring as scoring_module
import scanner.universe as universe_module

for _module in (
    alpaca_client_module,
    scanner_config,
    indicators_module,
    inspector_module,
    fundamentals_module,
    leadership_module,
    regime_module,
    scoring_module,
    universe_module,
    audit_module,
):
    importlib.reload(_module)

AlpacaClient = alpaca_client_module.AlpacaClient
AlpacaCredentials = alpaca_client_module.AlpacaCredentials
ScannerConfig = scanner_config.ScannerConfig
MARKET_SYMBOLS = scanner_config.MARKET_SYMBOLS
SECTOR_ETFS = scanner_config.SECTOR_ETFS
QUALITY_PRESETS = scanner_config.QUALITY_PRESETS
add_indicators = indicators_module.add_indicators
latest_snapshot = indicators_module.latest_snapshot
normalize_ticker = inspector_module.normalize_ticker
resolve_asset = inspector_module.resolve_asset
in_selected_universe = inspector_module.in_selected_universe
pct_rank_against_reference = inspector_module.pct_rank_against_reference
zero_to_100_rank_against_reference = inspector_module.zero_to_100_rank_against_reference
liquidity_diagnostic = inspector_module.liquidity_diagnostic
inspector_authority = inspector_module.inspector_authority
AUTO_REFERENCE_LABEL = inspector_module.AUTO_REFERENCE_LABEL
resolve_reference_universe = inspector_module.resolve_reference_universe
reference_signature = inspector_module.reference_signature
scan_reference_compatible = inspector_module.scan_reference_compatible
reference_coverage = inspector_module.reference_coverage
reference_confidence = inspector_module.reference_confidence
reference_is_usable = inspector_module.reference_is_usable
fetch_sec_ticker_map = fundamentals_module.fetch_sec_ticker_map
resolve_sec_identity = fundamentals_module.resolve_sec_identity
fetch_sec_identity_mirror = fundamentals_module.fetch_sec_identity_mirror
SEC_IDENTITY_MIRROR_LABEL = fundamentals_module.SEC_IDENTITY_MIRROR_LABEL
SecAccessError = fundamentals_module.SecAccessError
SecIdentityNotFound = fundamentals_module.SecIdentityNotFound
build_sec_declared_user_agent = fundamentals_module.build_sec_declared_user_agent
classify_sec_transport_failure = fundamentals_module.classify_sec_transport_failure
fetch_sec_companyfacts = fundamentals_module.fetch_sec_companyfacts
build_fundamental_snapshot = fundamentals_module.build_fundamental_snapshot
unavailable_fundamental_snapshot = fundamentals_module.unavailable_snapshot
normalize_sec_ticker = fundamentals_module.normalize_sec_ticker
DEFAULT_SEC_USER_AGENT = fundamentals_module.DEFAULT_SEC_USER_AGENT
add_leadership_features = leadership_module.add_leadership_features
aggregate_regime = regime_module.aggregate_regime
with_breadth = regime_module.with_breadth
build_cross_section = scoring_module.build_cross_section
apply_quality_filters = scoring_module.apply_quality_filters
score_universe = scoring_module.score_universe
UNIVERSE_OPTIONS = universe_module.UNIVERSE_OPTIONS
fetch_universe = universe_module.fetch_universe
build_funnel = audit_module.build_funnel
bucket_integrity = audit_module.bucket_integrity
liquidity_summary = audit_module.liquidity_summary


APP_VERSION = "V1.2.2.1b1"

st.set_page_config(
    page_title=f"ALPACA Scanner {APP_VERSION}",
    page_icon="📈",
    layout="wide",
)
st.title(f"📈 ALPACA Scanner {APP_VERSION}")
st.caption(
    "Regime-aware swing scanner • 15-min delayed SIP / consolidated historical SIP "
    "• Trade With Edge • Candidate Quality Engine • Fundamental Growth & Earnings Quality • SEC Fair Access Connectivity Validation"
)
st.caption(
    "Roadmap stage: V1.2 Candidate Quality Engine → V1.2.2.1b1 SEC Fair "
    "Access / CompanyFacts Connectivity Validation • Financial values remain "
    "official SEC CompanyFacts • Fundamental model remains SHADOW MODE • "
    "Frozen scanner classifications remain unchanged"
)


def secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


@st.cache_resource
def get_client():
    key = secret("APCA_API_KEY_ID")
    sec = secret("APCA_API_SECRET_KEY")
    if not key or not sec:
        return None

    return AlpacaClient(
        AlpacaCredentials(
            key_id=key,
            secret_key=sec,
            paper_base_url=secret(
                "APCA_PAPER_BASE_URL",
                "https://paper-api.alpaca.markets",
            ),
            data_base_url=secret(
                "APCA_DATA_BASE_URL",
                "https://data.alpaca.markets",
            ),
            feed=secret("APCA_DATA_FEED", "delayed_sip"),
            historical_feed=secret("APCA_HISTORICAL_FEED", "sip"),
        )
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_assets(_client):
    return _client.get_assets()


@st.cache_data(ttl=900, show_spinner=False)
def load_prev_daily_bars(_client, syms, bs):
    return _client.get_previous_daily_bars(list(syms), batch_size=bs)


@st.cache_data(ttl=600, show_spinner=False)
def load_bars(_client, syms, days, bs):
    return _client.get_daily_bars(list(syms), days=days, batch_size=bs)


@st.cache_data(ttl=21600, show_spinner=False)
def load_named_universe(name):
    return fetch_universe(name)


@st.cache_data(ttl=86400, show_spinner=False)
def resolve_sec_identity_cached(ticker, user_agent):
    # Cache the successful per-ticker identity so Streamlit reruns do not
    # repeatedly download SEC association files.
    return resolve_sec_identity(
        ticker,
        user_agent=user_agent,
        timeout=12.0,
    )


@st.cache_data(ttl=86400, show_spinner=False)
def resolve_sec_identity_mirror_cached(ticker):
    mapping = fetch_sec_identity_mirror(timeout=15.0)
    identity = mapping.get(normalize_sec_ticker(ticker))
    if identity is None:
        raise SecIdentityNotFound(
            f"{normalize_sec_ticker(ticker)} was not found in the "
            "version-pinned SEC-derived identity mirror."
        )
    out = dict(identity)
    out["identity_source"] = SEC_IDENTITY_MIRROR_LABEL
    out["identity_authority"] = (
        "SEC-DERIVED MIRROR / FINANCIALS STILL OFFICIAL SEC"
    )
    out["identity_access_status"] = "PASS"
    out["identity_diagnostics"] = (
        "Official SEC identity route skipped when no declared Fair Access "
        "contact is configured."
    )
    return out


@st.cache_data(ttl=21600, show_spinner=False)
def load_sec_companyfacts_cached(cik, user_agent):
    return fetch_sec_companyfacts(
        cik,
        user_agent=user_agent,
        timeout=15.0,
    )


def load_fundamental_snapshot(symbol):
    """On-demand official SEC fundamentals; never changes scanner state."""
    ticker = normalize_sec_ticker(symbol)

    declared = build_sec_declared_user_agent(
        contact_email=secret("SEC_CONTACT_EMAIL"),
        explicit_user_agent=secret("SEC_USER_AGENT"),
        organization=secret("SEC_ORGANIZATION", "TradeWithEdge"),
    )
    user_agent = declared.get("user_agent", "")

    try:
        if declared["ready"]:
            identity = resolve_sec_identity_cached(ticker, user_agent)
        else:
            identity = resolve_sec_identity_mirror_cached(ticker)
    except SecIdentityNotFound as exc:
        return unavailable_fundamental_snapshot(
            ticker,
            str(exc),
            sec_access_status="IDENTITY NOT FOUND",
            fair_access_status=("PASS" if declared["ready"] else "CONFIG REQUIRED"),
            fair_access_source=declared.get("source"),
            fair_access_contact=declared.get("contact_email"),
            companyfacts_transport_diagnosis="NOT ATTEMPTED",
            identity_access_status="PASS / NOT FOUND",
            companyfacts_access_status="NOT ATTEMPTED",
        )
    except SecAccessError as exc:
        return unavailable_fundamental_snapshot(
            ticker,
            exc.compact(),
            sec_access_status="SEC IDENTITY ACCESS FAILED",
            fair_access_status=("PASS" if declared["ready"] else "CONFIG REQUIRED"),
            fair_access_source=declared.get("source"),
            fair_access_contact=declared.get("contact_email"),
            companyfacts_transport_diagnosis="NOT ATTEMPTED",
            identity_access_status="FAILED",
            companyfacts_access_status="NOT ATTEMPTED",
            identity_diagnostics=exc.compact(),
        )

    if not declared["ready"]:
        return unavailable_fundamental_snapshot(
            ticker,
            declared["reason"],
            cik=identity["cik"],
            company_name=identity.get("title"),
            sec_access_status="SEC FAIR ACCESS CONFIG REQUIRED",
            fair_access_status="CONFIG REQUIRED",
            fair_access_source=declared.get("source"),
            fair_access_contact=None,
            companyfacts_transport_diagnosis="NOT ATTEMPTED",
            identity_access_status="PASS",
            companyfacts_access_status="NOT ATTEMPTED",
            identity_source=identity.get("identity_source"),
            identity_authority=identity.get("identity_authority"),
            identity_diagnostics=identity.get("identity_diagnostics", ""),
        )

    try:
        companyfacts = load_sec_companyfacts_cached(identity["cik"], user_agent)
    except SecAccessError as exc:
        diagnosis = classify_sec_transport_failure(
            stage=exc.stage,
            status_code=exc.status_code,
            declaration_ready=True,
        )
        return unavailable_fundamental_snapshot(
            ticker,
            exc.compact(),
            cik=identity["cik"],
            company_name=identity.get("title"),
            sec_access_status="SEC COMPANYFACTS ACCESS FAILED",
            fair_access_status="PASS",
            fair_access_source=declared.get("source"),
            fair_access_contact=declared.get("contact_email"),
            companyfacts_transport_diagnosis=diagnosis,
            identity_access_status="PASS",
            companyfacts_access_status="FAILED",
            identity_source=identity.get("identity_source"),
            identity_authority=identity.get("identity_authority"),
            identity_diagnostics=identity.get("identity_diagnostics", ""),
        )
    except Exception as exc:
        return unavailable_fundamental_snapshot(
            ticker,
            f"Unexpected SEC CompanyFacts failure: {exc}",
            cik=identity["cik"],
            company_name=identity.get("title"),
            sec_access_status="SEC COMPANYFACTS ACCESS FAILED",
            fair_access_status="PASS",
            fair_access_source=declared.get("source"),
            fair_access_contact=declared.get("contact_email"),
            companyfacts_transport_diagnosis="UNEXPECTED CLIENT FAILURE",
            identity_access_status="PASS",
            companyfacts_access_status="FAILED",
            identity_source=identity.get("identity_source"),
            identity_authority=identity.get("identity_authority"),
            identity_diagnostics=identity.get("identity_diagnostics", ""),
        )

    snapshot = build_fundamental_snapshot(
        ticker,
        companyfacts,
        cik=identity["cik"],
        company_name=identity.get("title"),
    )
    snapshot["identity_source"] = identity.get("identity_source")
    snapshot["identity_authority"] = identity.get("identity_authority")
    snapshot["identity_access_status"] = "PASS"
    snapshot["companyfacts_access_status"] = "PASS"
    snapshot["sec_access_status"] = "PASS"
    snapshot["fair_access_status"] = "PASS"
    snapshot["fair_access_source"] = declared.get("source")
    snapshot["fair_access_contact"] = declared.get("contact_email")
    snapshot["companyfacts_transport_diagnosis"] = "PASS"
    snapshot["identity_diagnostics"] = identity.get("identity_diagnostics", "")
    return snapshot


def _symbol_key(symbol):
    """Canonical comparison key for external index/ETF vs Alpaca tickers."""
    return "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())


def _money_m(value):
    if value is None or pd.isna(value):
        return "—"
    return f"${float(value) / 1_000_000:,.1f}M"


def _money_m2(value):
    """Two-decimal $M formatter for audit-boundary precision."""
    if value is None or pd.isna(value):
        return "—"
    return f"${float(value) / 1_000_000:,.2f}M"


def _pct(numerator, denominator):
    if not denominator:
        return 0.0
    return 100.0 * float(numerator) / float(denominator)


def liquid_universe(client, cfg, selected_symbols=None):
    """Apply Alpaca tradability + completed-session consolidated SIP gates.

    Returns the deep-scan selection plus a complete audit dictionary. The audit
    keeps the *true* liquidity-pass count separate from the deep-scan cap.
    """
    selected_keys = (
        {_symbol_key(s) for s in selected_symbols}
        if selected_symbols
        else None
    )

    valid = []
    for asset in load_assets(client):
        if not (
            asset.get("tradable")
            and asset.get("status") == "active"
            and asset.get("exchange") in {"NASDAQ", "NYSE", "ARCA", "AMEX"}
        ):
            continue

        symbol = asset.get("symbol", "")
        if not symbol or len(symbol) > 10 or "/" in symbol:
            continue

        if selected_keys is not None and _symbol_key(symbol) not in selected_keys:
            continue

        valid.append(symbol)

    # Audit named-universe membership explicitly. No silent disappearance:
    # list source-universe symbols that did not match an active/tradable Alpaca
    # U.S. equity after the same canonical-symbol normalization used above.
    if selected_symbols:
        matched_keys = {_symbol_key(s) for s in valid}
        unmatched_symbols = [
            s for s in selected_symbols if _symbol_key(s) not in matched_keys
        ]
    else:
        unmatched_symbols = []

    prev_bars = load_prev_daily_bars(
        client,
        tuple(valid),
        cfg.snapshot_batch_size,
    )

    observations = []
    for symbol in valid:
        bar = prev_bars.get(symbol) or {}
        px = bar.get("c")
        vol = bar.get("v")
        bar_ts = bar.get("t")

        if px is None or vol is None:
            continue

        try:
            px = float(px)
            vol = float(vol)
        except Exception:
            continue

        if px <= 0 or vol < 0:
            continue

        dollar_volume = px * vol
        passed_price = px >= cfg.min_price
        passed_liquidity = passed_price and dollar_volume >= cfg.min_prev_dollar_volume

        observations.append(
            {
                "symbol": symbol,
                "bar_timestamp": bar_ts,
                "snapshot_price": px,
                "previous_volume": vol,
                "prev_dollar_volume": dollar_volume,
                "passed_price": passed_price,
                "passed_liquidity": passed_liquidity,
            }
        )

    obs = pd.DataFrame(observations)
    if obs.empty:
        passed = pd.DataFrame(
            columns=["symbol", "snapshot_price", "prev_dollar_volume"]
        )
        price_pass_count = 0
        liquidity_pass_count = 0
    else:
        price_pass_count = int(obs["passed_price"].sum())
        full_pass = obs[obs["passed_liquidity"]].copy()
        liquidity_pass_count = int(len(full_pass))
        passed = (
            full_pass.sort_values("prev_dollar_volume", ascending=False)
            .head(cfg.max_deep_scan_symbols)
            [["symbol", "snapshot_price", "prev_dollar_volume"]]
            .reset_index(drop=True)
        )

    diag = liquidity_summary(obs, cfg.min_prev_dollar_volume)
    audit = {
        "matched_count": len(valid),
        "unmatched_symbols": unmatched_symbols,
        "sip_bar_count": len(prev_bars),
        "usable_sip_count": len(obs),
        "missing_sip_count": max(len(valid) - len(prev_bars), 0),
        "unusable_sip_count": max(len(prev_bars) - len(obs), 0),
        "price_pass_count": price_pass_count,
        "liquidity_pass_count": liquidity_pass_count,
        "deep_scan_count": len(passed),
        "deep_scan_capped": liquidity_pass_count > cfg.max_deep_scan_symbols,
        "q25": diag["q25"],
        "median": diag["median"],
        "q75": diag["q75"],
        "cutoff_sample": diag["cutoff_sample"],
    }
    return passed, audit



def _fund_pct(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}%"


def _fund_pp(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{100.0 * float(value):+.1f}pp"


def render_fundamental_quality(symbol, *, expanded=True, key_prefix="fund"):
    """Render V1.2.2.1b1 fundamentals in read-only SHADOW MODE."""
    with st.spinner(f"Loading official SEC fundamentals for {symbol}..."):
        fund = load_fundamental_snapshot(symbol)

    with st.expander(
        "V1.2.2.1b1 Fundamental Growth & Earnings Quality — Explainable View",
        expanded=expanded,
    ):
        st.caption(
            "SHADOW MODE: official SEC financial-performance diagnostics are "
            "displayed for validation only. They do NOT yet change Persistent "
            "Quality, Candidate Quality, Leadership, Entry Quality, buckets, "
            "or trade decisions. Earnings/event DATE reliability remains a "
            "separate roadmap layer."
        )

        f1, f2, f3, f4 = st.columns(4)
        f1.metric(
            "Fundamental Quality (shadow)",
            (
                f"{fund['fundamental_score']:.1f}/100"
                if pd.notna(fund.get("fundamental_score"))
                else "N/A"
            ),
        )
        f2.metric("Fundamental grade", fund.get("fundamental_grade", "N/A"))
        f3.metric(
            "Fundamental Data Confidence",
            fund.get("fundamental_confidence", "UNKNOWN"),
        )
        f4.metric(
            "Metric coverage",
            f"{fund.get('available_weight_pct', 0):.0f}%",
        )

        st.markdown("#### SEC Fair Access & Connectivity")
        a1, a2, a3 = st.columns(3)
        a1.metric(
            "Fair Access declaration",
            fund.get("fair_access_status", "UNKNOWN"),
        )
        a2.metric(
            "Ticker → CIK",
            fund.get("identity_access_status", "UNKNOWN"),
        )
        a3.metric(
            "CompanyFacts",
            fund.get("companyfacts_access_status", "UNKNOWN"),
        )

        b1, b2, b3 = st.columns(3)
        b1.metric(
            "Transport diagnosis",
            fund.get("companyfacts_transport_diagnosis", "UNKNOWN"),
        )
        b2.metric(
            "Identity source",
            fund.get("identity_source") or "—",
        )
        b3.metric(
            "Declared contact",
            fund.get("fair_access_contact") or "—",
        )

        identity_authority = fund.get("identity_authority")
        if identity_authority:
            if "MIRROR" in str(identity_authority).upper():
                st.info(
                    "Ticker → CIK was resolved through a version-pinned "
                    "SEC-derived transport mirror because the deployment path "
                    "to www.sec.gov is blocked. Revenue, earnings, filing dates "
                    "and all financial facts are still requested ONLY from "
                    "official data.sec.gov CompanyFacts."
                )
            else:
                st.caption(f"Identity authority: {identity_authority}")

        if fund.get("fair_access_status") == "CONFIG REQUIRED":
            st.warning(
                "SEC CompanyFacts has NOT been requested yet. A declared "
                "Fair Access contact email is required. Configure the "
                "Streamlit secret SEC_CONTACT_EMAIL, then inspect the ticker "
                "again. N/A values are not financial conclusions while this "
                "status is shown."
            )
        elif fund.get("sec_access_status") != "PASS":
            st.error(
                "SEC CompanyFacts access did not complete. This is a "
                "connectivity/transport result, NOT evidence that the company "
                "lacks fundamentals. Diagnosis: "
                + str(
                    fund.get("companyfacts_transport_diagnosis")
                    or "UNKNOWN"
                )
            )
            if fund.get("access_detail"):
                st.caption("Technical detail: " + str(fund["access_detail"]))
        elif fund.get("identity_diagnostics"):
            st.caption(
                "SEC identity fallback diagnostics: "
                + str(fund.get("identity_diagnostics"))
            )


        st.markdown("#### Revenue growth")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Latest quarter YoY", _fund_pct(fund.get("revenue_q_yoy")))
        r2.metric(
            "Previous quarter YoY",
            _fund_pct(fund.get("revenue_q_prior_yoy")),
        )
        r3.metric(
            "Growth change",
            _fund_pp(fund.get("revenue_q_change")),
        )
        rev_valid = int(fund.get("revenue_valid_count", 0) or 0)
        rev_pos = int(fund.get("revenue_positive_count", 0) or 0)
        r4.metric(
            "Recent positive YoY reads",
            f"{rev_pos}/{rev_valid}" if rev_valid else "—",
        )

        if (
            pd.notna(fund.get("revenue_q_prior_yoy"))
            and pd.notna(fund.get("revenue_q_yoy"))
            and pd.notna(fund.get("revenue_q_change"))
        ):
            rev_state = (
                "ACCELERATING"
                if fund["revenue_q_change"] >= 0.05
                else "DECELERATING"
                if fund["revenue_q_change"] <= -0.05
                else "STABLE"
            )
            st.caption(
                "Revenue momentum: "
                f"{_fund_pct(fund['revenue_q_prior_yoy'])} → "
                f"{_fund_pct(fund['revenue_q_yoy'])} "
                f"({_fund_pp(fund['revenue_q_change'])}) — {rev_state}."
            )

        st.markdown("#### Earnings growth")
        e1, e2, e3, e4 = st.columns(4)
        earnings_metric = fund.get("earnings_metric", "Earnings")
        latest_earnings = (
            _fund_pct(fund.get("earnings_q_yoy"))
            if pd.notna(fund.get("earnings_q_yoy"))
            else fund.get("earnings_q_state", "N/A")
        )
        e1.metric(f"Latest quarter YoY • {earnings_metric}", latest_earnings)
        e2.metric(
            "Previous quarter YoY",
            _fund_pct(fund.get("earnings_q_prior_yoy")),
        )
        e3.metric(
            "Growth change",
            _fund_pp(fund.get("earnings_q_change")),
        )
        earn_valid = int(fund.get("earnings_valid_count", 0) or 0)
        earn_pos = int(fund.get("earnings_positive_count", 0) or 0)
        e4.metric(
            "Recent positive YoY reads",
            f"{earn_pos}/{earn_valid}" if earn_valid else "—",
        )

        if (
            pd.notna(fund.get("earnings_q_prior_yoy"))
            and pd.notna(fund.get("earnings_q_yoy"))
            and pd.notna(fund.get("earnings_q_change"))
        ):
            earn_state = (
                "ACCELERATING"
                if fund["earnings_q_change"] >= 0.05
                else "DECELERATING"
                if fund["earnings_q_change"] <= -0.05
                else "STABLE"
            )
            st.caption(
                f"{earnings_metric} momentum: "
                f"{_fund_pct(fund['earnings_q_prior_yoy'])} → "
                f"{_fund_pct(fund['earnings_q_yoy'])} "
                f"({_fund_pp(fund['earnings_q_change'])}) — {earn_state}."
            )

        st.markdown("#### Longer-term confirmation")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric(
            "Latest FY revenue YoY",
            _fund_pct(fund.get("revenue_annual_yoy")),
        )
        annual_earn = (
            _fund_pct(fund.get("earnings_annual_yoy"))
            if pd.notna(fund.get("earnings_annual_yoy"))
            else fund.get("earnings_annual_state", "N/A")
        )
        a2.metric(f"Latest FY • {earnings_metric}", annual_earn)
        a3.metric(
            "Latest filing used",
            (
                str(fund.get("latest_filed"))
                if fund.get("latest_filed")
                else "—"
            ),
        )
        a4.metric(
            "SEC issuer / CIK",
            (
                f"{fund.get('ticker')} / {int(fund['cik']):010d}"
                if fund.get("cik") is not None
                else "—"
            ),
        )

        if fund.get("fundamental_reasons"):
            st.write(
                "**Fundamental strengths:** "
                + str(fund["fundamental_reasons"])
            )
        if fund.get("fundamental_risks"):
            st.warning(
                "Fundamental watch-outs: "
                + str(fund["fundamental_risks"])
            )

        source_detail = (
            f"Revenue concept: {fund.get('revenue_taxonomy') or '—'}:"
            f"{fund.get('revenue_concept') or '—'} • "
            f"Earnings concept: {fund.get('earnings_taxonomy') or '—'}:"
            f"{fund.get('earnings_concept') or '—'}"
        )
        st.caption(
            f"Source: {fund.get('source', 'SEC EDGAR CompanyFacts')} • "
            f"{source_detail} • No third-party fundamental fallback."
        )

    return fund

def chart(df, symbol):
    g = add_indicators(df)
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=g["timestamp"],
            open=g["open"],
            high=g["high"],
            low=g["low"],
            close=g["close"],
            name=symbol,
        )
    )

    for col, name in [
        ("ema8", "EMA8"),
        ("ema20", "EMA20"),
        ("ma50", "MA50"),
        ("ma200", "MA200"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=g["timestamp"],
                y=g[col],
                name=name,
            )
        )

    fig.update_layout(height=540, xaxis_rangeslider_visible=False)
    return fig


client = get_client()
if not client:
    st.error("Alpaca credentials are not configured.")
    st.info(
        "Add APCA_API_KEY_ID and APCA_API_SECRET_KEY in "
        "Streamlit Cloud → App settings → Secrets."
    )
    st.stop()


# -----------------------------------------------------------------------------
# Ticker Inspector explicit-action state.
# Typing a ticker alone does NOT open the Inspector.
# Only "Inspect ticker" activates it; only "Clear inspector" deactivates it.
# Run Scanner has NO authority over Inspector visibility/state.
# -----------------------------------------------------------------------------
if "scan" not in st.session_state:
    st.session_state.scan = None
if "inspector_ticker" not in st.session_state:
    st.session_state.inspector_ticker = ""
if "inspector_requested" not in st.session_state:
    st.session_state.inspector_requested = False
if "inspector_expanded" not in st.session_state:
    st.session_state.inspector_expanded = True
if "inspector_query_input" not in st.session_state:
    st.session_state.inspector_query_input = st.session_state.inspector_ticker


def _submit_inspector_callback():
    normalized = normalize_ticker(
        st.session_state.get("inspector_query_input", "")
    )
    st.session_state.inspector_ticker = normalized
    st.session_state.inspector_requested = bool(normalized)
    st.session_state.inspector_expanded = True


def _clear_inspector_callback():
    st.session_state.inspector_query_input = ""
    st.session_state.inspector_ticker = ""
    st.session_state.inspector_requested = False
    st.session_state.inspector_expanded = False


with st.sidebar:
    st.header("Scanner controls")

    universe_name = st.selectbox("Stock universe", UNIVERSE_OPTIONS, index=0)
    preset = st.selectbox(
        "Quality mode",
        ["BALANCED", "STRICT", "ELITE", "CUSTOM"],
        index=1,
    )

    min_price = st.number_input("Minimum price", 1.0, 500.0, 5.0, 1.0)
    min_prev_dv = st.number_input(
        "Minimum previous-day $ volume (M)", 1.0, 500.0, 20.0, 5.0
    )
    max_symbols = st.selectbox(
        "Maximum deep-scan symbols",
        [500, 1000, 1500, 2000, 3000],
        index=3,
    )

    if preset != "CUSTOM":
        pset = QUALITY_PRESETS[preset]
        min_avg_dv = pset["min_avg_dollar_volume_20d"] / 1_000_000
        min_avg_vol = pset["min_avg_volume_20d"] / 1_000_000
        min_atr = pset["min_atr_pct"]
        max_atr = pset["max_atr_pct"]
        min_rs = pset["min_rs_percentile"]

        st.caption(
            f"{preset}: 20D $Vol ≥ ${min_avg_dv:.0f}M • "
            f"20D Vol ≥ {min_avg_vol:.2f}M • "
            f"ATR {min_atr:.1f}-{max_atr:.1f}% • RS ≥ {min_rs:.0f}"
        )
    else:
        with st.expander("Advanced quality filters", expanded=True):
            min_avg_dv = st.number_input(
                "Minimum 20D avg $ volume (M)", 1.0, 500.0, 20.0, 5.0
            )
            min_avg_vol = st.number_input(
                "Minimum 20D avg share volume (M)", 0.05, 20.0, 0.50, 0.05
            )
            min_atr = st.number_input("Minimum ATR %", 0.1, 20.0, 1.5, 0.1)
            max_atr = st.number_input("Maximum ATR %", 1.0, 30.0, 10.0, 0.5)
            min_rs = st.number_input(
                "Minimum RS percentile", 0.0, 100.0, 60.0, 5.0
            )

    with st.expander("Trend gates"):
        require_above_ma50 = st.toggle("Require price > MA50", value=False)
        require_ma50_above_ma200 = st.toggle(
            "Require MA50 > MA200", value=False
        )

    strict = st.toggle("Strict earnings/event gate", value=True)
    run = st.button("🚀 Run Scanner", type="primary", use_container_width=True)

    st.divider()
    st.subheader("🔎 Ticker Inspector")
    st.caption(
        "Inspect any active Alpaca U.S. equity without changing the scanner "
        "universe, audit funnel, or candidate buckets."
    )
    inspector_reference_choice = st.selectbox(
        "Reference universe",
        [AUTO_REFERENCE_LABEL] + list(UNIVERSE_OPTIONS),
        index=0,
        help=(
            "AUTO uses the current Stock universe. A completed compatible scan "
            "is reused; otherwise the Inspector builds a cached read-only peer "
            "reference automatically."
        ),
    )
    ticker_query = st.text_input(
        "Ticker symbol",
        placeholder="AMZN",
        max_chars=15,
        key="inspector_query_input",
        help=(
            "Typing a ticker does not open the Inspector. "
            "Click Inspect ticker to analyze it."
        ),
    )
    inspect_submit = st.button(
        "Inspect ticker",
        use_container_width=True,
        key="inspect_ticker_button",
        on_click=_submit_inspector_callback,
    )
    clear_inspector = st.button(
        "Clear inspector",
        use_container_width=True,
        key="clear_inspector_button",
        help="Hide and clear the Inspector without changing scanner results.",
        on_click=_clear_inspector_callback,
    )


cfg = ScannerConfig(
    min_price=min_price,
    min_prev_dollar_volume=min_prev_dv * 1_000_000,
    min_avg_dollar_volume_20d=min_avg_dv * 1_000_000,
    min_avg_volume_20d=min_avg_vol * 1_000_000,
    min_atr_pct=min_atr,
    max_atr_pct=max_atr,
    min_rs_percentile=min_rs,
    require_above_ma50=require_above_ma50,
    require_ma50_above_ma200=require_ma50_above_ma200,
    max_deep_scan_symbols=max_symbols,
    strict_event_gate=strict,
)

inspector_reference_universe = resolve_reference_universe(
    universe_name,
    inspector_reference_choice,
)
inspector_reference_signature = reference_signature(
    inspector_reference_universe,
    cfg.min_price,
    cfg.min_prev_dollar_volume,
    cfg.max_deep_scan_symbols,
    cfg.history_days,
)



@st.cache_data(ttl=900, show_spinner=False)
def build_inspector_reference_cached(
    _client,
    _cfg,
    reference_universe_name,
    cache_signature,
):
    """Build the same peer cross-section used by scanner scoring, read-only."""
    uinfo = load_named_universe(reference_universe_name)
    selected_symbols = uinfo.symbols
    universe_member_count = len(selected_symbols) if selected_symbols else None

    regime_syms = list(dict.fromkeys(MARKET_SYMBOLS + list(SECTOR_ETFS.keys())))
    regime_bars = load_bars(
        _client,
        tuple(regime_syms),
        _cfg.history_days,
        _cfg.bar_batch_size,
    )
    regime = aggregate_regime(regime_bars, MARKET_SYMBOLS)

    universe_df, liquidity_audit = liquid_universe(
        _client,
        _cfg,
        selected_symbols,
    )
    if universe_df is None or universe_df.empty:
        raise RuntimeError(
            "No securities passed the selected reference universe/liquidity gates."
        )

    bars = load_bars(
        _client,
        tuple(universe_df["symbol"].tolist()),
        _cfg.history_days,
        _cfg.bar_batch_size,
    )
    if bars is None or bars.empty:
        raise RuntimeError(
            "No consolidated SIP history was returned for the reference universe."
        )

    spy = latest_snapshot(regime_bars[regime_bars["symbol"] == "SPY"])
    cross_section = build_cross_section(
        bars,
        spy.get("ret20"),
        spy.get("ret50"),
    )
    if cross_section is None or cross_section.empty:
        raise RuntimeError("Reference cross-section could not be constructed.")

    spy_bars = regime_bars[regime_bars["symbol"] == "SPY"].copy()
    cross_section = add_leadership_features(
        cross_section,
        bars,
        spy_bars,
    )

    deep_count = int(liquidity_audit.get("deep_scan_count", len(universe_df)))
    ref_count = int(len(cross_section))
    coverage = reference_coverage(ref_count, deep_count)
    confidence = reference_confidence(ref_count, deep_count)

    if not reference_is_usable(ref_count, deep_count):
        raise RuntimeError(
            f"Reference integrity gate failed: {ref_count:,}/{deep_count:,} "
            f"symbols produced usable cross-sectional history "
            f"({coverage:.1%} coverage). At least 20 peers and 90% coverage "
            "are required."
        )

    regime = with_breadth(regime, cross_section)

    return {
        "universe_name": reference_universe_name,
        "universe_info": uinfo,
        "universe_member_count": universe_member_count,
        "selected_symbols": selected_symbols,
        "regime": regime,
        "regime_bars": regime_bars,
        "bars": bars,
        "cross_section": cross_section,
        "liquidity_audit": liquidity_audit,
        "reference_signature": tuple(cache_signature),
        "reference_origin": "AUTO-BUILT / CACHED",
        "reference_count": ref_count,
        "reference_deep_count": deep_count,
        "reference_coverage": coverage,
        "reference_confidence": confidence,
        "ts": datetime.now(timezone.utc),
    }


def completed_scan_reference(scan):
    """Copy scan context and attach explicit reference metadata."""
    ctx = dict(scan)
    cross = ctx.get("cross_section")
    liq = ctx.get("liquidity_audit", {}) or {}
    ref_count = (
        int(len(cross))
        if cross is not None and not getattr(cross, "empty", True)
        else 0
    )
    deep_count = int(liq.get("deep_scan_count", ref_count))
    ctx["reference_origin"] = "COMPLETED SCAN"
    ctx["reference_count"] = ref_count
    ctx["reference_deep_count"] = deep_count
    ctx["reference_coverage"] = reference_coverage(ref_count, deep_count)
    ctx["reference_confidence"] = reference_confidence(ref_count, deep_count)
    return ctx


def resolve_inspector_reference(
    client,
    cfg,
    requested_universe,
    requested_signature,
    current_scan,
):
    """Reuse a compatible scan reference or auto-build a read-only one."""
    if scan_reference_compatible(
        current_scan,
        requested_universe,
        requested_signature,
    ):
        ctx = completed_scan_reference(current_scan)
        if reference_is_usable(
            ctx["reference_count"],
            ctx["reference_deep_count"],
        ):
            return ctx, None

    try:
        ctx = build_inspector_reference_cached(
            client,
            cfg,
            requested_universe,
            tuple(requested_signature),
        )
        return ctx, None
    except Exception as exc:
        return None, str(exc)


if run:
    progress = st.progress(0.03, text="Resolving selected universe...")

    try:
        uinfo = load_named_universe(universe_name)
    except Exception as exc:
        st.error(f"Universe source failed: {exc}")
        st.info(
            "No silent fallback was used. Select All U.S. Tradable / Liquid "
            "or retry later."
        )
        st.stop()

    selected_symbols = uinfo.symbols
    universe_member_count = len(selected_symbols) if selected_symbols else None

    progress.progress(0.10, text="Loading fixed U.S. market regime...")
    regime_syms = list(dict.fromkeys(MARKET_SYMBOLS + list(SECTOR_ETFS.keys())))

    try:
        regime_bars = load_bars(
            client,
            tuple(regime_syms),
            cfg.history_days,
            cfg.bar_batch_size,
        )
        regime = aggregate_regime(regime_bars, MARKET_SYMBOLS)
    except Exception as exc:
        st.error(f"Historical SIP regime stage failed. Details: {exc}")
        st.stop()

    progress.progress(
        0.20,
        text="Applying completed-session SIP price/liquidity gates...",
    )

    try:
        universe_df, liquidity_audit = liquid_universe(
            client,
            cfg,
            selected_symbols,
        )
    except Exception as exc:
        st.error(f"Consolidated SIP liquidity stage failed. Details: {exc}")
        st.info(
            "The scanner will not silently fall back to IEX-only volume, "
            "because that would understate true U.S. market liquidity."
        )
        st.stop()

    if universe_df.empty:
        st.warning("No securities passed the initial universe/liquidity gates.")
        st.caption(
            f"Matched to Alpaca: {liquidity_audit['matched_count']:,} • "
            f"Completed SIP bars: {liquidity_audit['sip_bar_count']:,} • "
            f"Passed price gate: {liquidity_audit['price_pass_count']:,} • "
            f"Passed liquidity: {liquidity_audit['liquidity_pass_count']:,}"
        )
        st.stop()

    progress.progress(
        0.38,
        text=(
            f"Deep scanning {len(universe_df):,} of "
            f"{liquidity_audit['liquidity_pass_count']:,} SIP-liquid symbols..."
        ),
    )

    try:
        bars = load_bars(
            client,
            tuple(universe_df["symbol"].tolist()),
            cfg.history_days,
            cfg.bar_batch_size,
        )
    except Exception as exc:
        st.error(f"Deep historical SIP scan failed. Details: {exc}")
        st.stop()
    history_returned_count = (
        int(bars["symbol"].nunique())
        if bars is not None and not bars.empty and "symbol" in bars.columns
        else 0
    )

    spy = latest_snapshot(regime_bars[regime_bars["symbol"] == "SPY"])
    cross_section = build_cross_section(
        bars,
        spy.get("ret20"),
        spy.get("ret50"),
    )

    # V1.2.1 — Leadership & Resilience Engine.
    # SHADOW MODE by design: the new leadership score is attached and audited,
    # but does not yet alter eligibility, buckets, or entry decisions.
    spy_bars = regime_bars[regime_bars["symbol"] == "SPY"].copy()
    cross_section = add_leadership_features(
        cross_section,
        bars,
        spy_bars,
    )

    history_min_count = (
        int((cross_section["bars"] >= cfg.min_history_bars).sum())
        if cross_section is not None
        and not cross_section.empty
        and "bars" in cross_section.columns
        else 0
    )

    # Market regime remains fixed. Selected-universe breadth and the 70/30
    # deployment blend are attached explicitly and separately.
    regime = with_breadth(regime, cross_section)
    deployment_score = regime.get("deployment_score", regime.get("score", 0))

    progress.progress(0.70, text="Auditing leadership, then applying persistent quality filters...")
    eligible, rejected = apply_quality_filters(cross_section, cfg)

    progress.progress(
        0.82,
        text=f"Scoring {len(eligible):,} persistent-quality symbols...",
    )
    scored = score_universe(eligible, deployment_score, cfg)

    if not scored.empty:
        scored = scored.merge(universe_df, on="symbol", how="left")

    bucket_audit = bucket_integrity(scored)
    starting_count = universe_member_count or liquidity_audit["matched_count"]

    funnel = build_funnel(
        [
            ("Starting universe", starting_count),
            ("Matched to Alpaca", liquidity_audit["matched_count"]),
            ("Completed SIP bars", liquidity_audit["sip_bar_count"]),
            (f"Price ≥ ${cfg.min_price:.2f}", liquidity_audit["price_pass_count"]),
            (
                f"Previous-day $ volume ≥ {_money_m(cfg.min_prev_dollar_volume)}",
                liquidity_audit["liquidity_pass_count"],
            ),
            ("Selected for deep scan", liquidity_audit["deep_scan_count"]),
            ("Deep history returned", history_returned_count),
            (f"History ≥ {cfg.min_history_bars} bars", history_min_count),
            ("Persistent quality-qualified", len(eligible)),
            ("Bucket-classified", bucket_audit["classified_count"]),
        ]
    )

    st.session_state.scan = {
        "regime": regime,
        "regime_bars": regime_bars,
        "bars": bars,
        "cross_section": cross_section,
        "scored": scored,
        "rejected": rejected,
        "universe_name": universe_name,
        "reference_signature": reference_signature(
            universe_name,
            cfg.min_price,
            cfg.min_prev_dollar_volume,
            cfg.max_deep_scan_symbols,
            cfg.history_days,
        ),
        "universe_info": uinfo,
        "universe_member_count": universe_member_count,
        "selected_symbols": selected_symbols,
        "liquidity_audit": liquidity_audit,
        "history_returned_count": history_returned_count,
        "history_min_count": history_min_count,
        "eligible_count": len(eligible),
        "bucket_audit": bucket_audit,
        "funnel": funnel,
        "ts": datetime.now(timezone.utc),
    }

    progress.progress(1.0, text="Scan complete")


def _inspector_leadership_row(ticker_row, ticker_bars, spy_bars, reference):
    """Score one ticker against the current scan's frozen V1.2.1 reference."""
    row = ticker_row.copy()

    # If already present in the scan reference, use the exact frozen row.
    if reference is not None and not reference.empty:
        existing = reference[reference["symbol"] == row["symbol"]]
        if not existing.empty and "leadership_score" in existing.columns:
            return existing.iloc[0].copy()

    raw = leadership_module._symbol_leadership_features(
        ticker_bars,
        spy_bars,
        -0.01,
        60,
        3,
    )
    for key, value in raw.items():
        row[key] = value

    if reference is None or reference.empty:
        row["leadership_score"] = float("nan")
        row["leadership_grade"] = "N/A"
        row["leadership_reasons"] = ""
        row["leadership_risks"] = (
            "No completed scanner cross-section is available for "
            "cross-sectional Leadership Score ranking."
        )
    else:
        ref = reference[reference["symbol"] != row["symbol"]].copy()

        row["lead_rs20_pct"] = zero_to_100_rank_against_reference(
            row.get("rs_vs_spy_20"), ref.get("rs_vs_spy_20", pd.Series(dtype=float))
        )
        row["lead_rs50_pct"] = zero_to_100_rank_against_reference(
            row.get("rs_vs_spy_50"), ref.get("rs_vs_spy_50", pd.Series(dtype=float))
        )
        row["lead_accel_pct"] = zero_to_100_rank_against_reference(
            row.get("rs_accel"), ref.get("rs_accel", pd.Series(dtype=float))
        )
        stress_excess_pct = zero_to_100_rank_against_reference(
            row.get("stress_excess_mean"),
            ref.get("stress_excess_mean", pd.Series(dtype=float)),
        )
        stress_win_pct = zero_to_100_rank_against_reference(
            row.get("stress_outperform_rate"),
            ref.get("stress_outperform_rate", pd.Series(dtype=float)),
        )
        row["lead_stress_excess_pct"] = stress_excess_pct
        row["lead_stress_win_pct"] = stress_win_pct
        row["lead_resilience_pct"] = (
            0.60 * stress_excess_pct + 0.40 * stress_win_pct
            if pd.notna(stress_excess_pct) and pd.notna(stress_win_pct)
            else stress_excess_pct if pd.notna(stress_excess_pct) else stress_win_pct
        )
        row["lead_rs_high_pct"] = zero_to_100_rank_against_reference(
            row.get("rs_line_high_gap"),
            ref.get("rs_line_high_gap", pd.Series(dtype=float)),
        )

        components = [
            ("lead_rs20_pct", 0.30),
            ("lead_rs50_pct", 0.25),
            ("lead_accel_pct", 0.15),
            ("lead_resilience_pct", 0.20),
            ("lead_rs_high_pct", 0.10),
        ]
        weighted = []
        weights = []
        for col, weight in components:
            value = row.get(col)
            if pd.notna(value):
                weighted.append(float(value) * weight)
                weights.append(weight)
        score = sum(weighted) / sum(weights) if weights else float("nan")
        row["leadership_score"] = score
        row["leadership_grade"] = leadership_module._grade(score)
        reasons, risks = leadership_module._explain(pd.Series(row))
        row["leadership_reasons"] = reasons
        row["leadership_risks"] = risks

    # User-facing forms retained even when full ranking is unavailable.
    for raw_col, display_col in [
        ("rs_vs_spy_20", "rs_vs_spy_20_pct"),
        ("rs_vs_spy_50", "rs_vs_spy_50_pct"),
        ("rs_vs_spy_100", "rs_vs_spy_100_pct"),
        ("rs20_10d_ago", "rs20_10d_ago_pct"),
        ("rs20_change_10d", "rs20_change_10d_pp"),
        ("stress_excess_mean", "stress_excess_mean_pct"),
        ("stress_outperform_rate", "stress_outperform_pct"),
    ]:
        value = row.get(raw_col)
        row[display_col] = 100.0 * float(value) if pd.notna(value) else float("nan")

    capture = row.get("downside_capture")
    row["downside_capture_pct"] = (
        100.0 * float(capture) if pd.notna(capture) else float("nan")
    )
    return row


def inspect_ticker(client, cfg, symbol, reference_scan=None):
    """Run an audit-safe single-ticker diagnostic.

    The inspector never mutates the frozen scanner result. When a completed scan
    is available, percentile-based RS/Leadership and legacy quality scoring use
    that scan as the reference distribution.
    """
    symbol = normalize_ticker(symbol)
    if not symbol:
        return {"error": "Enter a valid U.S. ticker symbol, for example AMZN."}

    asset = resolve_asset(load_assets(client), symbol)
    if asset is None:
        return {
            "error": (
                f"{symbol} could not be resolved to one unique active Alpaca "
                "U.S. equity."
            )
        }

    resolved = str(asset.get("symbol", symbol)).upper()
    active = asset.get("status") == "active"
    tradable = bool(asset.get("tradable"))
    exchange = asset.get("exchange", "—")

    if reference_scan is not None:
        reference_name = reference_scan.get("universe_name", "Current reference")
        selected_symbols = reference_scan.get("selected_symbols")
        if selected_symbols is None:
            try:
                selected_symbols = reference_scan["universe_info"].symbols
            except Exception:
                selected_symbols = None
        reference_cross = reference_scan.get("cross_section")
        regime_bars = reference_scan.get("regime_bars")
        regime = reference_scan.get("regime", {})
        reference_origin = reference_scan.get("reference_origin", "COMPLETED SCAN")
        reference_count = int(
            reference_scan.get(
                "reference_count",
                len(reference_cross)
                if reference_cross is not None
                and not getattr(reference_cross, "empty", True)
                else 0,
            )
        )
        reference_deep_count = int(
            reference_scan.get("reference_deep_count", reference_count)
        )
        reference_cov = float(
            reference_scan.get(
                "reference_coverage",
                reference_coverage(reference_count, reference_deep_count),
            )
        )
        reference_conf = reference_scan.get(
            "reference_confidence",
            reference_confidence(reference_count, reference_deep_count),
        )
    else:
        reference_name = "Reference unavailable"
        selected_symbols = None
        reference_cross = None
        reference_origin = "UNAVAILABLE"
        reference_count = 0
        reference_deep_count = 0
        reference_cov = 0.0
        reference_conf = "LOW"
        regime_syms = list(dict.fromkeys(MARKET_SYMBOLS + list(SECTOR_ETFS.keys())))
        regime_bars = load_bars(
            client,
            tuple(regime_syms),
            cfg.history_days,
            cfg.bar_batch_size,
        )
        regime = aggregate_regime(regime_bars, MARKET_SYMBOLS)

    membership = in_selected_universe(resolved, selected_symbols)

    prev = load_prev_daily_bars(client, (resolved,), cfg.snapshot_batch_size)
    liq = liquidity_diagnostic(
        prev.get(resolved),
        cfg.min_price,
        cfg.min_prev_dollar_volume,
    )

    ticker_bars = load_bars(
        client,
        (resolved,),
        cfg.history_days,
        cfg.bar_batch_size,
    )
    if ticker_bars is None or ticker_bars.empty:
        return {
            "error": f"No usable historical SIP daily bars were returned for {resolved}."
        }

    spy_bars = regime_bars[regime_bars["symbol"] == "SPY"].copy()
    spy_snapshot = latest_snapshot(spy_bars)

    one = build_cross_section(
        ticker_bars,
        spy_snapshot.get("ret20"),
        spy_snapshot.get("ret50"),
    )
    if one is None or one.empty:
        return {
            "error": (
                f"{resolved} does not have enough usable daily history to build "
                "the technical cross-section."
            )
        }

    row = one.iloc[0].copy()
    row["symbol"] = resolved

    if reference_cross is not None and not reference_cross.empty:
        existing = reference_cross[reference_cross["symbol"] == resolved]
        if not existing.empty:
            # Exact frozen reference row when this symbol was already deep-scanned.
            row = existing.iloc[0].copy()
        else:
            ref = reference_cross[reference_cross["symbol"] != resolved]
            row["rs20_pct"] = pct_rank_against_reference(
                row.get("rs20"), ref.get("rs20", pd.Series(dtype=float))
            )
            row["rs50_pct"] = pct_rank_against_reference(
                row.get("rs50"), ref.get("rs50", pd.Series(dtype=float))
            )
            row["rs_score"] = 0.60 * row["rs20_pct"] + 0.40 * row["rs50_pct"]

    leadership_row = _inspector_leadership_row(
        row,
        ticker_bars,
        spy_bars,
        reference_cross,
    )
    for key, value in leadership_row.items():
        row[key] = value

    has_reference = reference_cross is not None and not reference_cross.empty

    if has_reference:
        eligible_df, rejected_df = apply_quality_filters(
            pd.DataFrame([row]),
            cfg,
        )
        persistent_pass = not eligible_df.empty
        gate_reasons = (
            ""
            if persistent_pass
            else str(rejected_df.iloc[0].get("eligibility_reasons", ""))
        )
    else:
        persistent_pass = None
        gate_reasons = (
            "Cross-sectional RS reference required before persistent-quality "
            "eligibility can be determined."
        )

    deployment_score = regime.get("deployment_score", regime.get("score", 0))
    diagnostic_scored = score_universe(
        pd.DataFrame([row]),
        deployment_score,
        cfg,
    )
    scored_row = (
        diagnostic_scored.iloc[0].copy()
        if diagnostic_scored is not None and not diagnostic_scored.empty
        else pd.Series(dtype=object)
    )

    if not has_reference and not scored_row.empty:
        # Hard integrity gate: single-ticker/self-ranked RS must never leak into
        # official Candidate Quality or scanner classification.
        scored_row["quality_score"] = np.nan
        scored_row["quality_reasons"] = ""
        scored_row["bucket"] = "NOT RANKED"
        scored_row["decision"] = "NOT RANKED"

    return {
        "symbol": resolved,
        "asset": asset,
        "active": active,
        "tradable": tradable,
        "exchange": exchange,
        "reference_name": reference_name,
        "reference_origin": reference_origin,
        "reference_count": reference_count,
        "reference_deep_count": reference_deep_count,
        "reference_coverage": reference_cov,
        "reference_confidence": reference_conf,
        "membership": membership,
        "liquidity": liq,
        "bars": ticker_bars,
        "row": row,
        "persistent_pass": persistent_pass,
        "gate_reasons": gate_reasons,
        "diagnostic": scored_row,
        "has_reference": has_reference,
        "scan_ts": (
            reference_scan.get("ts") if reference_scan is not None else None
        ),
    }


def render_ticker_inspector(result, cfg, show_title=True):
    if result.get("error"):
        st.error(result["error"])
        return

    symbol = result["symbol"]
    row = result["row"]
    diag = result["diagnostic"]
    liq = result["liquidity"]

    authority = inspector_authority(
        result["has_reference"],
        result["persistent_pass"],
        liq["status"],
        diag.get("bucket") if not diag.empty else None,
    )

    if show_title:
        st.subheader(f"🔎 Ticker Inspector — {symbol}")
    if result["has_reference"]:
        st.caption(
            f"Cross-sectional reference: {result['reference_name']} • "
            f"{result['reference_origin']} • "
            f"N={result['reference_count']:,}/{result['reference_deep_count']:,} "
            f"({result['reference_coverage']:.1%} coverage) • "
            f"Reference Confidence: {result['reference_confidence']} • "
            "Read-only: scanner counts and buckets are not changed."
        )
    else:
        st.caption(
            f"Requested cross-sectional reference: "
            f"{result.get('requested_reference_name', result['reference_name'])} • "
            "Reference unavailable • Read-only: scanner counts and buckets are not changed."
        )

    i1, i2, i3, i4, i5, i6 = st.columns(6)
    i1.metric("Alpaca status", "ACTIVE" if result["active"] else "NOT ACTIVE")
    i2.metric("Tradable", "YES" if result["tradable"] else "NO")
    i3.metric("Exchange", result["exchange"])
    membership = result["membership"]
    i4.metric(
        "Reference-universe member",
        "ALL U.S." if membership is None else ("YES" if membership else "NO"),
    )
    i5.metric("SIP liquidity gate", liq["status"])
    i6.metric(
        "Persistent quality",
        authority["persistent_quality"],
    )

    if not result["has_reference"]:
        ref_error = result.get("reference_error")
        st.warning(
            "Automatic peer-reference construction did not produce a trusted "
            "cross-section. Direct technical, entry, and raw leadership "
            "diagnostics remain available, but percentile-dependent outputs "
            "stay REF REQUIRED as a fail-safe."
            + (f" Reference error: {ref_error}" if ref_error else "")
        )

    if liq["status"] != "PASS":
        st.warning("Initial liquidity gate: " + liq["reason"])

    if result["has_reference"] and result["persistent_pass"] is False:
        st.warning(
            "Persistent-quality gate: FAIL"
            + (f" — {result['gate_reasons']}" if result["gate_reasons"] else "")
        )
        st.caption(
            "Quality/entry values below are diagnostic only. A failed "
            "persistent-quality gate cannot become an official scanner candidate."
        )

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric(
        "Previous close",
        f"${liq['prev_close']:,.2f}" if pd.notna(liq["prev_close"]) else "—",
    )
    t2.metric(
        "Previous $ volume",
        _money_m2(liq["prev_dollar_volume"]),
    )
    t3.metric(
        "20D avg $ volume",
        _money_m(row.get("avg_dollar_volume20")),
    )
    t4.metric(
        "ATR %",
        f"{row.get('atr_pct'):.2f}%"
        if pd.notna(row.get("atr_pct"))
        else "—",
    )
    t5.metric(
        "History",
        f"{int(row.get('bars', 0))} bars",
    )

    st.markdown("#### Quality Engine snapshot")
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric(
        "Candidate Quality",
        (
            f"{diag.get('quality_score'):.1f}/100"
            if authority["candidate_quality_authoritative"]
            and pd.notna(diag.get("quality_score"))
            else "REF REQUIRED"
        ),
    )
    q2.metric(
        "Leadership",
        (
            f"{row.get('leadership_score'):.1f}/100"
            if authority["leadership_authoritative"]
            and pd.notna(row.get("leadership_score"))
            else "REF REQUIRED"
        ),
    )
    q3.metric(
        "Entry Quality" if result["has_reference"] else "Entry Quality (diagnostic)",
        f"{diag.get('entry_score'):.1f}/100"
        if pd.notna(diag.get("entry_score"))
        else "—",
    )
    q4.metric(
        "Legacy RS",
        (
            f"{row.get('rs_score'):.1f} %ile"
            if authority["legacy_rs_authoritative"]
            and pd.notna(row.get("rs_score"))
            else "REF REQUIRED"
        ),
    )
    q5.metric(
        "Inspector engine status",
        authority["official_status"],
    )

    if authority["candidate_quality_authoritative"] and pd.notna(diag.get("quality_score")):
        st.write(
            f"**Why quality:** {diag.get('quality_reasons', '') or '—'}"
        )
    if pd.notna(diag.get("entry_score")):
        st.write(
            f"**Why entry:** {diag.get('entry_reasons', '') or '—'}"
        )
        if diag.get("chase_reasons"):
            st.warning("Anti-chase gate: " + str(diag["chase_reasons"]))

    with st.expander(
        "Leadership & Resilience — Explainable View",
        expanded=True,
    ):
        l1, l2, l3, l4, l5 = st.columns(5)
        l1.metric(
            "Leadership grade",
            row.get("leadership_grade", "N/A")
            if result["has_reference"]
            else "REF REQUIRED",
        )
        l2.metric(
            "RS vs SPY • 20D",
            f"{row.get('rs_vs_spy_20_pct'):+.1f}%"
            if pd.notna(row.get("rs_vs_spy_20_pct"))
            else "—",
        )
        l3.metric(
            "RS vs SPY • 50D",
            f"{row.get('rs_vs_spy_50_pct'):+.1f}%"
            if pd.notna(row.get("rs_vs_spy_50_pct"))
            else "—",
        )
        l4.metric(
            "RS vs SPY • 100D",
            f"{row.get('rs_vs_spy_100_pct'):+.1f}%"
            if pd.notna(row.get("rs_vs_spy_100_pct"))
            else "—",
        )
        l5.metric(
            "Leadership Data Confidence",
            row.get("leadership_confidence", "LOW"),
        )

        old_rs20 = row.get("rs20_10d_ago_pct")
        now_rs20 = row.get("rs_vs_spy_20_pct")
        change_pp = row.get("rs20_change_10d_pp")
        if pd.notna(old_rs20) and pd.notna(now_rs20) and pd.notna(change_pp):
            state = (
                "ACCELERATING" if change_pp >= 1.0
                else "DECELERATING" if change_pp <= -1.0
                else "STABLE"
            )
            st.write(
                f"**Relative momentum:** RS20 {old_rs20:+.1f}% → "
                f"{now_rs20:+.1f}% over 10 sessions "
                f"({change_pp:+.1f}pp) — **{state}**"
            )

        stress_days = int(row.get("stress_day_count", 0) or 0)
        stress_wins = int(row.get("stress_win_count", 0) or 0)
        stress_rate = row.get("stress_outperform_pct")
        stress_excess = row.get("stress_excess_mean_pct")
        capture_pct = row.get("downside_capture_pct")
        capture_label = row.get("downside_capture_label", "N/A")
        st.write(
            "**Market stress:** "
            + (
                f"beat SPY {stress_wins}/{stress_days} sessions "
                f"({stress_rate:.0f}%), avg excess {stress_excess:+.2f}%, "
                f"downside capture {capture_pct:.0f}% — {capture_label}"
                if stress_days
                and pd.notna(stress_rate)
                and pd.notna(stress_excess)
                and pd.notna(capture_pct)
                else "insufficient stress data"
            )
        )
        if pd.notna(capture_pct):
            st.caption(
                f"On selected SPY stress sessions the stock lost about "
                f"{capture_pct / 100.0:.2f}× as much as SPY in aggregate."
            )

        rs_index = row.get("rs_line_index")
        rs_gap = row.get("rs_line_high_gap_pct")
        if pd.notna(rs_index) and pd.notna(rs_gap):
            st.write(
                f"**RS line:** {rs_index:.1f}/100 — "
                f"{abs(rs_gap):.1f}% below its 100D relative-strength peak."
            )

        st.write(
            f"**Leadership strengths:** "
            f"{row.get('leadership_reasons', '') or '—'}"
        )
        if row.get("leadership_risks"):
            st.warning(
                "Leadership watch-outs: "
                + str(row["leadership_risks"])
            )

    render_fundamental_quality(
        symbol,
        expanded=True,
        key_prefix="inspector_fund",
    )

    if not result["has_reference"]:
        st.info(
            "Inspector conclusion: DIRECT DIAGNOSTICS ONLY — automatic "
            "reference construction failed its integrity gate, so percentile-"
            "dependent quality/leadership/eligibility remains blocked."
        )
    elif result["persistent_pass"] and liq["status"] == "PASS":
        st.success(
            f"Inspector conclusion: {diag.get('decision', '—')} • "
            f"Bucket: {diag.get('bucket', '—')}"
        )
    else:
        st.info(
            "Inspector conclusion: diagnostic only — this ticker does not "
            "currently satisfy every scanner gate."
        )

    st.plotly_chart(
        chart(result["bars"], symbol),
        use_container_width=True,
        key=f"inspector_chart_{symbol}",
    )



res = st.session_state.scan

if st.session_state.inspector_requested:
    if not st.session_state.inspector_ticker:
        st.error("Enter a valid ticker symbol, for example AMZN.")
    else:
        try:
            with st.spinner(
                f"Preparing {inspector_reference_universe} peer reference..."
            ):
                inspector_reference_ctx, inspector_reference_error = (
                    resolve_inspector_reference(
                        client,
                        cfg,
                        inspector_reference_universe,
                        inspector_reference_signature,
                        res,
                    )
                )

            inspector_result = inspect_ticker(
                client,
                cfg,
                st.session_state.inspector_ticker,
                inspector_reference_ctx,
            )
            inspector_result["requested_reference_name"] = (
                inspector_reference_universe
            )
            inspector_result["reference_error"] = inspector_reference_error

            if inspector_result.get("error"):
                inspector_label = (
                    f"🔎 Ticker Inspector — "
                    f"{st.session_state.inspector_ticker} | ERROR"
                )
            else:
                authority = inspector_authority(
                    inspector_result["has_reference"],
                    inspector_result["persistent_pass"],
                    inspector_result["liquidity"]["status"],
                    inspector_result["diagnostic"].get("bucket")
                    if not inspector_result["diagnostic"].empty
                    else None,
                )
                lead_grade = (
                    inspector_result["row"].get("leadership_grade", "N/A")
                    if inspector_result["has_reference"]
                    else "REF REQUIRED"
                )
                legacy_rs = inspector_result["row"].get("rs_score")
                rs_label = (
                    f"{legacy_rs:.1f}%ile"
                    if inspector_result["has_reference"] and pd.notna(legacy_rs)
                    else "REF REQUIRED"
                )
                inspector_label = (
                    f"🔎 Ticker Inspector — {inspector_result['symbol']} | "
                    f"{authority['official_status']} | Leadership {lead_grade} | "
                    f"RS {rs_label}"
                )

            with st.expander(
                inspector_label,
                expanded=st.session_state.inspector_expanded,
            ):
                render_ticker_inspector(
                    inspector_result,
                    cfg,
                    show_title=False,
                )
            st.divider()
        except Exception as exc:
            st.error(f"Ticker Inspector failed safely: {exc}")
            st.caption(
                "The scanner result was not changed. Ticker Inspector is "
                "read-only by design."
            )

if not res:
    st.info(
        "Ticker Inspector is self-contained: it automatically builds/reuses "
        "the selected peer reference for complete cross-sectional scoring. "
        "Run Scanner only when you want the full universe audit and candidate dashboard."
    )
    st.stop()

regime = res["regime"]
scored = res["scored"]
liq = res["liquidity_audit"]
bucket_audit = res["bucket_audit"]


# -----------------------------------------------------------------------------
# 1) Scanner audit integrity
# -----------------------------------------------------------------------------
st.subheader("1) Universe & Scanner Audit")

u1, u2, u3, u4, u5, u6 = st.columns(6)
u1.metric("Selected universe", res["universe_name"])
u2.metric(
    "Universe members",
    f'{res["universe_member_count"]:,}'
    if res["universe_member_count"]
    else f'{liq["matched_count"]:,} Alpaca active',
)
u3.metric("Matched to Alpaca", f'{liq["matched_count"]:,}')
u4.metric("Passed SIP liquidity", f'{liq["liquidity_pass_count"]:,}')
u5.metric("Deep-scanned", f'{liq["deep_scan_count"]:,}')
u6.metric("Persistent quality", f'{res["eligible_count"]:,}')

st.caption(
    f'Source: {res["universe_info"].source} • '
    f'Type: {res["universe_info"].source_type} • '
    f'{res["universe_info"].note}'
)

if liq["deep_scan_capped"]:
    st.warning(
        f"Deep-scan cap active: {liq['liquidity_pass_count']:,} securities passed "
        f"the SIP liquidity gate, but only the top {liq['deep_scan_count']:,} by "
        "previous-session dollar volume were deep-scanned."
    )

st.info(
    "Data integrity: previous-day liquidity uses the last fully completed "
    f"{client.creds.historical_feed.upper()} daily bar; deep history uses "
    f"{client.creds.historical_feed.upper()} with a ≥20-minute cutoff. "
    f"Latest/snapshot feed configured as {client.creds.feed.upper()}. "
    "IEX-only volume is not used for consolidated liquidity gates."
)

with st.expander("🔎 Scanner Audit Integrity", expanded=True):
    if bucket_audit["reconciled"] and bucket_audit["classified_count"] == res["eligible_count"]:
        st.success(
            "PASS — every persistent-quality symbol is accounted for in exactly "
            f"one candidate bucket ({bucket_audit['classified_count']:,}/"
            f"{res['eligible_count']:,})."
        )
    else:
        st.error(
            "FAIL — candidate accounting does not reconcile. "
            f"Quality-qualified: {res['eligible_count']:,}; "
            f"classified: {bucket_audit['classified_count']:,}; "
            f"unknown bucket rows: {bucket_audit['unknown_count']:,}."
        )
        if bucket_audit["unknown_buckets"]:
            st.write("Unknown buckets:", ", ".join(bucket_audit["unknown_buckets"]))

    funnel_view = res["funnel"].copy()
    for col in ["% of prior stage", "% of starting universe"]:
        funnel_view[col] = funnel_view[col].map(
            lambda x: "—" if pd.isna(x) else f"{float(x):.1f}%"
        )
    st.dataframe(funnel_view, use_container_width=True, hide_index=True)

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric(
        "Usable SIP coverage",
        f'{_pct(liq["usable_sip_count"], liq["matched_count"]):.1f}%',
        help="Usable completed-session SIP bars divided by Alpaca-matched symbols.",
    )
    d2.metric("Missing SIP bars", f'{liq["missing_sip_count"]:,}')
    d3.metric("Prev $Vol P25", _money_m(liq["q25"]))
    d4.metric("Prev $Vol median", _money_m(liq["median"]))
    d5.metric("Prev $Vol P75", _money_m(liq["q75"]))

    unmatched = liq.get("unmatched_symbols", [])
    if unmatched:
        with st.expander(
            f"Unmatched universe symbols ({len(unmatched):,})",
            expanded=False,
        ):
            st.caption(
                "These source-universe symbols did not match an active/tradable "
                "Alpaca U.S. equity after canonical symbol normalization."
            )
            st.dataframe(
                pd.DataFrame({"symbol": unmatched}),
                use_container_width=True,
                hide_index=True,
            )

    cutoff = liq["cutoff_sample"]
    if cutoff is not None and not cutoff.empty:
        st.caption(
            "Securities nearest the previous-session dollar-volume cutoff — "
            "use this to sanity-check the SIP liquidity boundary."
        )
        cutoff_view = cutoff[
            [
                "symbol",
                "bar_timestamp",
                "snapshot_price",
                "previous_volume",
                "prev_dollar_volume",
                "liquidity_status",
            ]
        ].copy()
        cutoff_view = cutoff_view.rename(
            columns={"snapshot_price": "prev_close"}
        )
        cutoff_view["prev_close"] = cutoff_view["prev_close"].map(
            lambda x: f"${x:,.2f}"
        )
        cutoff_view["previous_volume"] = cutoff_view["previous_volume"].map(
            lambda x: f"{x:,.0f}"
        )
        cutoff_view["prev_dollar_volume"] = cutoff_view["prev_dollar_volume"].map(
            _money_m2
        )
        st.dataframe(cutoff_view, use_container_width=True, hide_index=True)

    if res["rejected"] is not None and not res["rejected"].empty:
        reason_counts = (
            res["rejected"]["eligibility_reasons"]
            .fillna("")
            .str.split("; ")
            .explode()
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(10)
        )
        if not reason_counts.empty:
            st.caption("Top persistent-quality rejection reasons")
            st.dataframe(
                reason_counts.rename("count").to_frame(),
                use_container_width=True,
            )


# -----------------------------------------------------------------------------
# 2) Market regime, selected-universe breadth, deployment regime
# -----------------------------------------------------------------------------
st.subheader("2) Market & Deployment Regime")

breadth = regime.get("breadth", {})
r1, r2, r3, r4 = st.columns(4)
r1.metric("U.S. Market Regime", regime["label"])
r2.metric("Market score", f'{regime["score"]:.0f}/100')
r3.metric(
    "Selected-universe breadth",
    f'{breadth.get("breadth_score", 0):.1f}/100' if breadth else "—",
)
r4.metric(
    "Deployment score",
    f'{regime.get("deployment_score", regime["score"]):.0f}/100',
)

if breadth:
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("% > EMA20", f'{breadth["above_ema20_pct"]:.1f}%')
    b2.metric("% > MA50", f'{breadth["above_ma50_pct"]:.1f}%')
    b3.metric("% > MA200", f'{breadth["above_ma200_pct"]:.1f}%')
    b4.metric(
        "% > EMA20 & MA50",
        f'{breadth["above_ema20_and_ma50_pct"]:.1f}%',
    )

st.caption(
    "U.S. Market Regime is fixed from SPY/QQQ/IWM and does not change merely "
    "because a different stock universe is selected. Deployment score = 70% "
    "market regime + 30% selected-universe breadth."
)
st.info(
    f"Deployment: {regime.get('deployment_label', regime['label'])} • "
    f"Exposure: {regime.get('deployment_exposure', regime['exposure'])}"
)


# -----------------------------------------------------------------------------
# V1.2.1 Quality Engine — leadership/resilience shadow validation
# -----------------------------------------------------------------------------
st.subheader("3) Candidate Quality Engine — Leadership & Resilience (Explainable)")
st.info(
    "V1.2.1.1 SHADOW MODE: Leadership & Resilience is calculated independently "
    "and displayed for validation. It does NOT yet change persistent-quality "
    "eligibility, candidate buckets, entry quality, or trade decisions."
)

lead_valid = scored["leadership_score"].dropna() if "leadership_score" in scored.columns else pd.Series(dtype=float)
if not lead_valid.empty:
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Leadership median", f"{lead_valid.median():.1f}/100")
    q2.metric("A / A+ leadership", f"{int((lead_valid >= 80).sum()):,}")
    q3.metric("Elite A+ ≥90", f"{int((lead_valid >= 90).sum()):,}")
    high_conf = (
        int((scored["leadership_confidence"] == "HIGH").sum())
        if "leadership_confidence" in scored.columns
        else 0
    )
    q4.metric("High Leadership Data Confidence", f"{high_conf:,}/{len(scored):,}")

    st.caption(
        "Leadership composite: 30% RS20 + 25% RS50 + 15% RS acceleration + "
        "20% SPY-pullback resilience + 10% RS-line proximity to its 100D high."
    )

st.markdown("### 3B) Fundamental Quality — Revenue & Earnings")
st.info(
    "V1.2.2.1b1 SHADOW MODE: fundamentals are loaded on demand for the selected "
    "candidate or Ticker Inspector from official SEC EDGAR CompanyFacts. "
    "This first validation build does not batch-fetch fundamentals for the "
    "entire universe and does not alter scanner eligibility or ranking."
)

# -----------------------------------------------------------------------------
# 4) Candidate accounting and buckets
# -----------------------------------------------------------------------------
st.subheader("4) Swing Candidates")

if scored is None or scored.empty:
    st.warning(
        "No symbols passed all persistent-quality filters. "
        "NO TRADE is a valid result."
    )
    st.stop()

bucket_display = {
    "ACTIONABLE NOW": "ACTIONABLE NOW",
    "TECH + EVENT CHECK": "TECH ACTIONABLE — EVENT CHECK",
    "A-QUALITY — WAIT": "A-QUALITY — WAIT",
    "WAIT / ENTRY NOT READY": "WAIT",
    "DEVELOPING": "DEVELOPING",
    "AVOID / BROKEN": "AVOID / BROKEN",
    "ALL": "ALL",
}

counts = bucket_audit["counts"]
count_cols = st.columns(6)
metric_labels = [
    ("ACTIONABLE NOW", "ACTIONABLE NOW"),
    ("TECH + EVENT CHECK", "TECH ACTIONABLE — EVENT CHECK"),
    ("A-QUALITY — WAIT", "A-QUALITY — WAIT"),
    ("WAIT / ENTRY NOT READY", "WAIT"),
    ("DEVELOPING", "DEVELOPING"),
    ("AVOID / BROKEN", "AVOID / BROKEN"),
]
for i, (display, code) in enumerate(metric_labels):
    count_cols[i].metric(display, counts.get(code, 0))

st.caption(
    "Bucket reconciliation: "
    f"{bucket_audit['classified_count']:,} classified = "
    f"{res['eligible_count']:,} persistent-quality qualified."
)

bucket_label = st.radio(
    "Bucket",
    list(bucket_display.keys()),
    horizontal=True,
)
bucket_code = bucket_display[bucket_label]
view = scored if bucket_code == "ALL" else scored[scored["bucket"] == bucket_code]

cols = [
    "symbol",
    "bucket",
    "setup",
    "quality_score",
    "leadership_score",
    "leadership_grade",
    "entry_score",
    "rs_score",
    "rs_vs_spy_20_pct",
    "rs_vs_spy_50_pct",
    "rs_vs_spy_100_pct",
    "rs20_10d_ago_pct",
    "rs20_change_10d_pp",
    "stress_win_count",
    "stress_day_count",
    "stress_outperform_pct",
    "stress_excess_mean_pct",
    "downside_capture_pct",
    "downside_capture_label",
    "rs_line_index",
    "rs_line_high_gap_pct",
    "leadership_confidence",
    "close",
    "atr_pct",
    "avg_dollar_volume20",
    "ext_ema8_pct",
    "ext_ema20_pct",
    "ext_atr",
    "vol_ratio",
    "entry_px",
    "stop",
    "t1",
    "t2",
    "event_confidence",
    "quality_reasons",
    "entry_reasons",
    "chase_reasons",
]

st.dataframe(
    view[[c for c in cols if c in view.columns]].head(150),
    use_container_width=True,
    hide_index=True,
)


# -----------------------------------------------------------------------------
# 4) Candidate detail
# -----------------------------------------------------------------------------
st.subheader("5) Candidate Detail")

sel = st.selectbox("Symbol", scored["symbol"].head(100).tolist())
row = scored[scored["symbol"] == sel].iloc[0]
symbol_bars = res["bars"][res["bars"]["symbol"] == sel]

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Candidate Quality", f'{row["quality_score"]:.1f}/100')
m2.metric(
    "Leadership (shadow)",
    f'{row.get("leadership_score", float("nan")):.1f}/100'
    if pd.notna(row.get("leadership_score"))
    else "—",
)
m3.metric("Entry Quality", f'{row["entry_score"]:.1f}/100')
m4.metric("Legacy RS", f'{row["rs_score"]:.1f} %ile')
m5.metric("Decision", row["decision"])

st.write(f'**Why quality:** {row.get("quality_reasons", "") or "—"}')
st.write(f'**Why entry:** {row.get("entry_reasons", "") or "—"}')

with st.expander("V1.2.1.1 Leadership & Resilience — Explainable View", expanded=True):
    st.markdown("#### Relative leadership")
    l1, l2, l3, l4, l5 = st.columns(5)
    l1.metric("Leadership grade", row.get("leadership_grade", "N/A"))
    l2.metric(
        "RS vs SPY • 20D",
        f'{row.get("rs_vs_spy_20_pct", float("nan")):+.1f}%'
        if pd.notna(row.get("rs_vs_spy_20_pct"))
        else "—",
        help="Stock return relative to SPY over the latest 20 trading sessions.",
    )
    l3.metric(
        "RS vs SPY • 50D",
        f'{row.get("rs_vs_spy_50_pct", float("nan")):+.1f}%'
        if pd.notna(row.get("rs_vs_spy_50_pct"))
        else "—",
        help="Intermediate-term relative performance versus SPY.",
    )
    l4.metric(
        "RS vs SPY • 100D",
        f'{row.get("rs_vs_spy_100_pct", float("nan")):+.1f}%'
        if pd.notna(row.get("rs_vs_spy_100_pct"))
        else "—",
        help="Longer-term leadership context. Display-only in V1.2.1.1; it does not change the validated Leadership Score.",
    )
    l5.metric(
        "Leadership Data Confidence",
        row.get("leadership_confidence", "LOW"),
        help="Confidence in the leadership calculation, not confidence in the trade.",
    )

    st.markdown("#### Relative momentum change")
    old_rs20 = row.get("rs20_10d_ago_pct")
    new_rs20 = row.get("rs_vs_spy_20_pct")
    change_pp = row.get("rs20_change_10d_pp")

    if pd.notna(old_rs20) and pd.notna(new_rs20) and pd.notna(change_pp):
        if change_pp >= 1.0:
            momentum_state = "ACCELERATING"
        elif change_pp <= -1.0:
            momentum_state = "DECELERATING"
        else:
            momentum_state = "STABLE"

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("RS20 • 10 sessions ago", f"{old_rs20:+.1f}%")
        a2.metric("RS20 • now", f"{new_rs20:+.1f}%")
        a3.metric("10-session change", f"{change_pp:+.1f}pp")
        a4.metric("Momentum state", momentum_state)

        st.caption(
            f"Interpretation: 20-day relative performance versus SPY moved "
            f"from {old_rs20:+.1f}% to {new_rs20:+.1f}% over the latest "
            f"10 trading sessions ({change_pp:+.1f} percentage points)."
        )
    else:
        st.caption("Insufficient aligned data for the 10-session RS20 comparison.")

    st.markdown("#### Market-stress resilience")
    stress_days = int(row.get("stress_day_count", 0) or 0)
    stress_wins = int(row.get("stress_win_count", 0) or 0)
    stress_rate = row.get("stress_outperform_pct")
    stress_excess = row.get("stress_excess_mean_pct")
    capture_pct = row.get("downside_capture_pct")
    capture_label = row.get("downside_capture_label", "N/A")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("SPY stress sessions", f"{stress_days}")
    s2.metric(
        "Beat SPY on stress days",
        f"{stress_wins}/{stress_days} ({stress_rate:.0f}%)"
        if stress_days and pd.notna(stress_rate)
        else "—",
    )
    s3.metric(
        "Avg excess return vs SPY",
        f"{stress_excess:+.2f}%"
        if pd.notna(stress_excess)
        else "—",
    )
    s4.metric(
        "Downside capture",
        f"{capture_pct:.0f}% — {capture_label}"
        if pd.notna(capture_pct)
        else "—",
    )

    if pd.notna(capture_pct):
        st.caption(
            f"Downside-capture interpretation: on the selected SPY stress "
            f"sessions, this stock lost about {capture_pct / 100.0:.2f}× "
            f"as much as SPY in aggregate. Below 100% means better downside "
            f"resilience than SPY; above 100% means worse."
        )

    st.markdown("#### Relative-strength line")
    rs_index = row.get("rs_line_index")
    rs_gap = row.get("rs_line_high_gap_pct")
    r1, r2 = st.columns(2)
    r1.metric(
        "RS-line index vs 100D peak",
        f"{rs_index:.1f}/100"
        if pd.notna(rs_index)
        else "—",
        help="100 means the stock/SPY relative-strength line is at its 100-day peak.",
    )
    r2.metric(
        "Distance below 100D RS peak",
        f"{abs(rs_gap):.1f}%"
        if pd.notna(rs_gap)
        else "—",
    )
    if pd.notna(rs_index) and pd.notna(rs_gap):
        st.caption(
            f"Interpretation: the stock/SPY relative-strength line is currently "
            f"{rs_index:.1f}/100, which is {abs(rs_gap):.1f}% below its best "
            f"relative level of the last 100 trading sessions."
        )

    st.write(
        f'**Leadership strengths:** '
        f'{row.get("leadership_reasons", "") or "—"}'
    )
    if row.get("leadership_risks"):
        st.warning("Leadership watch-outs: " + str(row["leadership_risks"]))

    st.caption(
        f'Stress mode: {row.get("stress_mode", "—")} • '
        "THRESHOLD means genuine SPY ≤ -1% sessions were available. "
        "Shadow-mode score still does not alter candidate classification."
    )

render_fundamental_quality(
    sel,
    expanded=True,
    key_prefix="candidate_fund",
)

if row["chase_reasons"]:
    st.warning("Anti-chase gate: " + row["chase_reasons"])

if row["event_confidence"] == "UNKNOWN":
    st.warning(
        "Event Data Confidence: UNKNOWN. Verify earnings/event timing before any action."
    )

p1, p2, p3, p4 = st.columns(4)
p1.metric("Entry ref", f'${row["entry_px"]:.2f}')
p2.metric("Stop", f'${row["stop"]:.2f}')
p3.metric("T1", f'${row["t1"]:.2f}')
p4.metric("T2", f'${row["t2"]:.2f}')

st.plotly_chart(chart(symbol_bars, sel), use_container_width=True)

st.caption(
    f'Latest/snapshot feed: {client.creds.feed.upper()} • '
    f'Historical feed: {client.creds.historical_feed.upper()} (≥20m delayed) • '
    f'Scan UTC: {res["ts"].strftime("%Y-%m-%d %H:%M:%S")} • '
    'Paper orders disabled. Scanner output is research, not execution.'
)
