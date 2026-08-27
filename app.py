import importlib
import os
from datetime import datetime, timezone

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
import scanner.leadership as leadership_module
import scanner.regime as regime_module
import scanner.scoring as scoring_module
import scanner.universe as universe_module

for _module in (
    alpaca_client_module,
    scanner_config,
    indicators_module,
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


APP_VERSION = "V1.2.1.1"

st.set_page_config(
    page_title=f"ALPACA Scanner {APP_VERSION}",
    page_icon="📈",
    layout="wide",
)
st.title(f"📈 ALPACA Scanner {APP_VERSION}")
st.caption(
    "Regime-aware swing scanner • 15-min delayed SIP / consolidated historical SIP "
    "• Trade With Edge • Candidate Quality Engine • Leadership Interpretability Polish"
)
st.caption(
    "Roadmap stage: V1.2 Candidate Quality Engine → V1.2.1.1 Leadership "
    "Interpretability Polish (shadow validation)"
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


if "scan" not in st.session_state:
    st.session_state.scan = None


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
        "universe_info": uinfo,
        "universe_member_count": universe_member_count,
        "liquidity_audit": liquidity_audit,
        "history_returned_count": history_returned_count,
        "history_min_count": history_min_count,
        "eligible_count": len(eligible),
        "bucket_audit": bucket_audit,
        "funnel": funnel,
        "ts": datetime.now(timezone.utc),
    }

    progress.progress(1.0, text="Scan complete")


res = st.session_state.scan
if not res:
    st.info("Click **Run Scanner** to begin.")
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
