import os
from datetime import datetime, timezone
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from scanner.alpaca_client import AlpacaClient, AlpacaCredentials

# Streamlit hot-reload guard: force scanner.config to refresh after multi-file GitHub updates.
import importlib
import scanner.config as scanner_config
scanner_config = importlib.reload(scanner_config)
ScannerConfig = scanner_config.ScannerConfig
MARKET_SYMBOLS = scanner_config.MARKET_SYMBOLS
SECTOR_ETFS = scanner_config.SECTOR_ETFS
QUALITY_PRESETS = scanner_config.QUALITY_PRESETS

from scanner.indicators import add_indicators, latest_snapshot
from scanner.regime import aggregate_regime, with_breadth
from scanner.scoring import build_cross_section, apply_quality_filters, score_universe
from scanner.universe import UNIVERSE_OPTIONS, fetch_universe

st.set_page_config(page_title="ALPACA Scanner V1.1", page_icon="📈", layout="wide")
st.title("📈 ALPACA Scanner V1.1")
st.caption("Regime-aware swing scanner • delayed/IEX-compatible • Trade With Edge")

def secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

@st.cache_resource
def get_client():
    key, sec = secret("APCA_API_KEY_ID"), secret("APCA_API_SECRET_KEY")
    if not key or not sec:
        return None
    return AlpacaClient(AlpacaCredentials(
        key_id=key, secret_key=sec,
        paper_base_url=secret("APCA_PAPER_BASE_URL","https://paper-api.alpaca.markets"),
        data_base_url=secret("APCA_DATA_BASE_URL","https://data.alpaca.markets"),
        feed=secret("APCA_DATA_FEED","iex"),
    ))

@st.cache_data(ttl=3600, show_spinner=False)
def load_assets(_client):
    return _client.get_assets()

@st.cache_data(ttl=900, show_spinner=False)
def load_snaps(_client, syms, bs):
    return _client.get_snapshots(list(syms), batch_size=bs)

@st.cache_data(ttl=600, show_spinner=False)
def load_bars(_client, syms, days, bs):
    return _client.get_daily_bars(list(syms), days=days, batch_size=bs)

@st.cache_data(ttl=21600, show_spinner=False)
def load_named_universe(name):
    return fetch_universe(name)

def liquid_universe(client, cfg, selected_symbols=None):
    selected = set(selected_symbols) if selected_symbols else None
    valid=[]
    for a in load_assets(client):
        if a.get("tradable") and a.get("status")=="active" and a.get("exchange") in {"NASDAQ","NYSE","ARCA","AMEX"}:
            s=a.get("symbol","")
            if s and len(s)<=8 and "/" not in s and (selected is None or s in selected):
                valid.append(s)

    snaps=load_snaps(client,tuple(valid),cfg.snapshot_batch_size)
    rows=[]
    for s in valid:
        q=snaps.get(s) or {}
        prev=q.get("prevDailyBar") or {}
        daily=q.get("dailyBar") or {}
        trade=q.get("latestTrade") or {}
        px=trade.get("p") or daily.get("c") or prev.get("c")
        vol=prev.get("v") or 0
        if px and float(px)>=cfg.min_price and float(px)*float(vol)>=cfg.min_prev_dollar_volume:
            rows.append((s,float(px),float(px)*float(vol)))

    if not rows:
        return pd.DataFrame(columns=["symbol","snapshot_price","prev_dollar_volume"])
    return (pd.DataFrame(rows,columns=["symbol","snapshot_price","prev_dollar_volume"])
            .sort_values("prev_dollar_volume",ascending=False)
            .head(cfg.max_deep_scan_symbols))

def chart(df,s):
    g=add_indicators(df)
    fig=go.Figure()
    fig.add_trace(go.Candlestick(
        x=g["timestamp"],open=g["open"],high=g["high"],low=g["low"],close=g["close"],name=s
    ))
    for c,n in [("ema8","EMA8"),("ema20","EMA20"),("ma50","MA50"),("ma200","MA200")]:
        fig.add_trace(go.Scatter(x=g["timestamp"],y=g[c],name=n))
    fig.update_layout(height=540,xaxis_rangeslider_visible=False)
    return fig

client=get_client()
if not client:
    st.error("Alpaca credentials are not configured.")
    st.info("Add APCA_API_KEY_ID and APCA_API_SECRET_KEY in Streamlit Cloud → App settings → Secrets.")
    st.stop()

with st.sidebar:
    st.header("Scanner controls")
    universe_name = st.selectbox("Stock universe", UNIVERSE_OPTIONS, index=0)
    preset = st.selectbox("Quality mode", ["BALANCED","STRICT","ELITE","CUSTOM"], index=1)

    min_price=st.number_input("Minimum price",1.0,500.0,5.0,1.0)
    min_prev_dv=st.number_input("Minimum previous-day $ volume (M)",1.0,500.0,20.0,5.0)
    max_symbols=st.selectbox("Maximum deep-scan symbols",[500,1000,1500,2000,3000],index=3)

    if preset != "CUSTOM":
        pset = QUALITY_PRESETS[preset]
        min_avg_dv = pset["min_avg_dollar_volume_20d"]/1_000_000
        min_avg_vol = pset["min_avg_volume_20d"]/1_000_000
        min_atr = pset["min_atr_pct"]
        max_atr = pset["max_atr_pct"]
        min_rs = pset["min_rs_percentile"]
        st.caption(
            f"{preset}: 20D $Vol ≥ ${min_avg_dv:.0f}M • 20D Vol ≥ {min_avg_vol:.2f}M • "
            f"ATR {min_atr:.1f}-{max_atr:.1f}% • RS ≥ {min_rs:.0f}"
        )
    else:
        with st.expander("Advanced quality filters", expanded=True):
            min_avg_dv=st.number_input("Minimum 20D avg $ volume (M)",1.0,500.0,20.0,5.0)
            min_avg_vol=st.number_input("Minimum 20D avg share volume (M)",0.05,20.0,0.50,0.05)
            min_atr=st.number_input("Minimum ATR %",0.1,20.0,1.5,0.1)
            max_atr=st.number_input("Maximum ATR %",1.0,30.0,10.0,0.5)
            min_rs=st.number_input("Minimum RS percentile",0.0,100.0,60.0,5.0)

    with st.expander("Trend gates"):
        require_above_ma50=st.toggle("Require price > MA50",value=False)
        require_ma50_above_ma200=st.toggle("Require MA50 > MA200",value=False)

    strict=st.toggle("Strict earnings/event gate",value=True)
    run=st.button("🚀 Run Scanner",type="primary",use_container_width=True)

cfg=ScannerConfig(
    min_price=min_price,
    min_prev_dollar_volume=min_prev_dv*1_000_000,
    min_avg_dollar_volume_20d=min_avg_dv*1_000_000,
    min_avg_volume_20d=min_avg_vol*1_000_000,
    min_atr_pct=min_atr,
    max_atr_pct=max_atr,
    min_rs_percentile=min_rs,
    require_above_ma50=require_above_ma50,
    require_ma50_above_ma200=require_ma50_above_ma200,
    max_deep_scan_symbols=max_symbols,
    strict_event_gate=strict
)

if "scan" not in st.session_state:
    st.session_state.scan=None

if run:
    p=st.progress(0.03,text="Resolving selected universe...")

    try:
        uinfo=load_named_universe(universe_name)
    except Exception as exc:
        st.error(f"Universe source failed: {exc}")
        st.info("No silent fallback was used. Select All U.S. Tradable / Liquid or retry later.")
        st.stop()

    selected_symbols = uinfo.symbols
    universe_member_count = len(selected_symbols) if selected_symbols else None

    p.progress(0.10,text="Loading market regime...")
    regime_syms=list(dict.fromkeys(MARKET_SYMBOLS+list(SECTOR_ETFS.keys())))
    rb=load_bars(client,tuple(regime_syms),cfg.history_days,cfg.bar_batch_size)
    regime=aggregate_regime(rb,MARKET_SYMBOLS)

    p.progress(0.20,text="Applying price and previous-day liquidity gates...")
    u=liquid_universe(client,cfg,selected_symbols)

    if u.empty:
        st.warning("No securities passed the initial universe/liquidity gates.")
        st.stop()

    p.progress(0.38,text=f"Deep scanning {len(u):,} symbols...")
    bars=load_bars(client,tuple(u["symbol"].tolist()),cfg.history_days,cfg.bar_batch_size)

    spy=latest_snapshot(rb[rb["symbol"]=="SPY"])
    x=build_cross_section(bars,spy.get("ret20"),spy.get("ret50"))
    regime=with_breadth(regime,x)

    p.progress(0.70,text="Applying persistent quality filters...")
    eligible,rejected=apply_quality_filters(x,cfg)

    p.progress(0.82,text=f"Scoring {len(eligible):,} quality-qualified symbols...")
    scored=score_universe(eligible,regime["score"],cfg)
    if not scored.empty:
        scored=scored.merge(u,on="symbol",how="left")

    st.session_state.scan={
        "regime":regime,"regime_bars":rb,"bars":bars,
        "scored":scored,"rejected":rejected,
        "universe_name":universe_name,"universe_info":uinfo,
        "universe_member_count":universe_member_count,
        "initial_pass_count":len(u),"eligible_count":len(eligible),
        "ts":datetime.now(timezone.utc)
    }
    p.progress(1.0,text="Scan complete")

res=st.session_state.scan
if not res:
    st.info("Click **Run Scanner** to begin.")
    st.stop()

regime=res["regime"]
scored=res["scored"]

st.subheader("1) Universe Audit")
u1,u2,u3,u4=st.columns(4)
u1.metric("Selected universe",res["universe_name"])
u2.metric("Universe members",f'{res["universe_member_count"]:,}' if res["universe_member_count"] else "Alpaca active")
u3.metric("After initial liquidity",f'{res["initial_pass_count"]:,}')
u4.metric("Quality-qualified",f'{res["eligible_count"]:,}')
st.caption(
    f'Source: {res["universe_info"].source} • Type: {res["universe_info"].source_type} • '
    f'{res["universe_info"].note}'
)

st.subheader("2) Market Regime")
a,b,c=st.columns(3)
a.metric("Regime",regime["label"])
b.metric("Score",f'{regime["score"]:.0f}/100')
c.metric("Exposure",regime["exposure"])

breadth=regime.get("breadth",{})
if breadth:
    b1,b2,b3,b4=st.columns(4)
    b1.metric("% > EMA20",f'{breadth["above_ema20_pct"]:.1f}%')
    b2.metric("% > MA50",f'{breadth["above_ma50_pct"]:.1f}%')
    b3.metric("% > MA200",f'{breadth["above_ma200_pct"]:.1f}%')
    b4.metric("Breadth score",f'{breadth["breadth_score"]:.1f}/100')

st.subheader("3) Swing Candidates")
if scored is None or scored.empty:
    st.warning("No symbols passed all quality filters. NO TRADE is a valid result.")
    st.stop()

bucket_order=["ACTIONABLE NOW","TECH ACTIONABLE — EVENT CHECK","A-QUALITY — WAIT","DEVELOPING","AVOID / BROKEN","ALL"]
counts=scored["bucket"].value_counts().to_dict()
count_cols=st.columns(5)
labels=bucket_order[:-1]
for i,label in enumerate(labels):
    count_cols[i].metric(label.replace("TECH ACTIONABLE — EVENT CHECK","TECH + EVENT CHECK"),counts.get(label,0))

bucket=st.radio("Bucket",bucket_order,horizontal=True)
view=scored if bucket=="ALL" else scored[scored["bucket"]==bucket]

cols=[
    "symbol","bucket","setup","quality_score","entry_score","rs_score",
    "close","atr_pct","avg_dollar_volume20","ext_ema8_pct","ext_ema20_pct",
    "ext_atr","vol_ratio","entry_px","stop","t1","t2","event_confidence",
    "quality_reasons","entry_reasons","chase_reasons"
]
st.dataframe(view[[c for c in cols if c in view.columns]].head(150),
             use_container_width=True,hide_index=True)

st.subheader("4) Candidate Detail")
sel=st.selectbox("Symbol",scored["symbol"].head(100).tolist())
row=scored[scored["symbol"]==sel].iloc[0]
g=res["bars"][res["bars"]["symbol"]==sel]

m1,m2,m3,m4=st.columns(4)
m1.metric("Candidate Quality",f'{row["quality_score"]:.1f}/100')
m2.metric("Entry Quality",f'{row["entry_score"]:.1f}/100')
m3.metric("RS",f'{row["rs_score"]:.1f} %ile')
m4.metric("Decision",row["decision"])

st.write(f'**Why quality:** {row.get("quality_reasons","") or "—"}')
st.write(f'**Why entry:** {row.get("entry_reasons","") or "—"}')
if row["chase_reasons"]:
    st.warning("Anti-chase gate: "+row["chase_reasons"])
if row["event_confidence"]=="UNKNOWN":
    st.warning("Event Data Confidence: UNKNOWN. Verify earnings/event timing before any action.")

t1,t2,t3,t4=st.columns(4)
t1.metric("Entry ref",f'${row["entry_px"]:.2f}')
t2.metric("Stop",f'${row["stop"]:.2f}')
t3.metric("T1",f'${row["t1"]:.2f}')
t4.metric("T2",f'${row["t2"]:.2f}')

st.plotly_chart(chart(g,sel),use_container_width=True)
st.caption(
    f'Data feed: {client.creds.feed.upper()} • Scan UTC: {res["ts"].strftime("%Y-%m-%d %H:%M:%S")} • '
    'Paper orders disabled. Scanner output is research, not execution.'
)
