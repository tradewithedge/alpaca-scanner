import os
from datetime import datetime, timezone
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scanner.alpaca_client import AlpacaClient, AlpacaCredentials
from scanner.config import ScannerConfig, MARKET_SYMBOLS, SECTOR_ETFS
from scanner.indicators import add_indicators, latest_snapshot
from scanner.regime import aggregate_regime
from scanner.scoring import build_cross_section, score_universe

st.set_page_config(page_title="ALPACA Scanner", page_icon="📈", layout="wide")
st.title("📈 ALPACA Scanner")
st.caption("Regime-aware swing scanner • delayed/IEX-compatible • Trade With Edge")

def secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

@st.cache_resource
def get_client():
    key, sec = secret("APCA_API_KEY_ID"), secret("APCA_API_SECRET_KEY")
    if not key or not sec: return None
    return AlpacaClient(AlpacaCredentials(
        key_id=key, secret_key=sec,
        paper_base_url=secret("APCA_PAPER_BASE_URL","https://paper-api.alpaca.markets"),
        data_base_url=secret("APCA_DATA_BASE_URL","https://data.alpaca.markets"),
        feed=secret("APCA_DATA_FEED","iex"),
    ))

@st.cache_data(ttl=3600, show_spinner=False)
def load_assets(_client): return _client.get_assets()

@st.cache_data(ttl=900, show_spinner=False)
def load_snaps(_client, syms, bs): return _client.get_snapshots(list(syms), batch_size=bs)

@st.cache_data(ttl=600, show_spinner=False)
def load_bars(_client, syms, days, bs): return _client.get_daily_bars(list(syms), days=days, batch_size=bs)

def liquid_universe(client,cfg):
    valid=[]
    for a in load_assets(client):
        if a.get("tradable") and a.get("status")=="active" and a.get("exchange") in {"NASDAQ","NYSE","ARCA","AMEX"}:
            s=a.get("symbol","")
            if s and len(s)<=8 and "/" not in s: valid.append(s)
    snaps=load_snaps(client,tuple(valid),cfg.snapshot_batch_size)
    rows=[]
    for s in valid:
        q=snaps.get(s) or {}; prev=q.get("prevDailyBar") or {}; daily=q.get("dailyBar") or {}; trade=q.get("latestTrade") or {}
        px=trade.get("p") or daily.get("c") or prev.get("c"); vol=prev.get("v") or 0
        if px and float(px)>=cfg.min_price and float(px)*float(vol)>=cfg.min_prev_dollar_volume:
            rows.append((s,float(px),float(px)*float(vol)))
    return pd.DataFrame(rows,columns=["symbol","snapshot_price","prev_dollar_volume"]).sort_values("prev_dollar_volume",ascending=False).head(cfg.max_deep_scan_symbols)

def chart(df,s):
    g=add_indicators(df); fig=go.Figure()
    fig.add_trace(go.Candlestick(x=g["timestamp"],open=g["open"],high=g["high"],low=g["low"],close=g["close"],name=s))
    for c,n in [("ema8","EMA8"),("ema20","EMA20"),("ma50","MA50")]:
        fig.add_trace(go.Scatter(x=g["timestamp"],y=g[c],name=n))
    fig.update_layout(height=500,xaxis_rangeslider_visible=False)
    return fig

client=get_client()
if not client:
    st.error("Alpaca credentials are not configured.")
    st.info("Add APCA_API_KEY_ID and APCA_API_SECRET_KEY in Streamlit Cloud → App settings → Secrets.")
    st.stop()

with st.sidebar:
    st.header("Scanner controls")
    min_price=st.number_input("Minimum price",1.0,500.0,5.0,1.0)
    min_dv=st.number_input("Minimum previous-day $ volume (M)",1.0,500.0,20.0,5.0)
    max_symbols=st.selectbox("Deep-scan liquid universe",[300,600,1200,2000],index=2)
    strict=st.toggle("Strict earnings/event gate",value=True)
    run=st.button("🚀 Run Scanner",type="primary",use_container_width=True)

cfg=ScannerConfig(min_price=min_price,min_prev_dollar_volume=min_dv*1_000_000,max_deep_scan_symbols=max_symbols,strict_event_gate=strict)
if "scan" not in st.session_state: st.session_state.scan=None

if run:
    p=st.progress(0.05,text="Loading regime...")
    regime_syms=list(dict.fromkeys(MARKET_SYMBOLS+list(SECTOR_ETFS.keys())))
    rb=load_bars(client,tuple(regime_syms),cfg.history_days,cfg.bar_batch_size)
    regime=aggregate_regime(rb,MARKET_SYMBOLS)
    p.progress(0.20,text="Building liquid universe...")
    u=liquid_universe(client,cfg)
    p.progress(0.45,text=f"Deep scanning {len(u):,} symbols...")
    bars=load_bars(client,tuple(u["symbol"].tolist()),cfg.history_days,cfg.bar_batch_size)
    spy=latest_snapshot(rb[rb["symbol"]=="SPY"])
    x=build_cross_section(bars,spy.get("ret20"),spy.get("ret50"))
    scored=score_universe(x,regime["score"],cfg).merge(u,on="symbol",how="left")
    st.session_state.scan={"regime":regime,"regime_bars":rb,"bars":bars,"scored":scored,"ts":datetime.now(timezone.utc)}
    p.progress(1.0,text="Scan complete")

res=st.session_state.scan
if not res:
    st.info("Click **Run Scanner** to begin.")
    st.stop()

regime=res["regime"]; scored=res["scored"]
st.subheader("1) Market Regime")
a,b,c=st.columns(3)
a.metric("Regime",regime["label"]); b.metric("Score",f'{regime["score"]:.0f}/100'); c.metric("Exposure",regime["exposure"])

st.subheader("2) Swing Candidates")
bucket=st.radio("Bucket",["ACTIONABLE NOW","A-QUALITY — WAIT","DEVELOPING","AVOID / BROKEN","ALL"],horizontal=True)
view=scored if bucket=="ALL" else scored[scored["bucket"]==bucket]
cols=["symbol","bucket","setup","quality_score","entry_score","rs_score","close","ext_ema8_pct","ext_ema20_pct","ext_atr","vol_ratio","entry_px","stop","t1","t2","event_confidence","chase_reasons"]
st.dataframe(view[[c for c in cols if c in view.columns]].head(100),use_container_width=True,hide_index=True)

if scored.empty: st.stop()
st.subheader("3) Candidate Detail")
sel=st.selectbox("Symbol",scored["symbol"].head(50).tolist())
row=scored[scored["symbol"]==sel].iloc[0]; g=res["bars"][res["bars"]["symbol"]==sel]
m1,m2,m3,m4=st.columns(4)
m1.metric("Candidate Quality",f'{row["quality_score"]:.1f}/100')
m2.metric("Entry Quality",f'{row["entry_score"]:.1f}/100')
m3.metric("RS",f'{row["rs_score"]:.1f} %ile')
m4.metric("Decision",row["decision"])
if row["chase_reasons"]: st.warning("Anti-chase gate: "+row["chase_reasons"])
if row["event_confidence"]=="UNKNOWN": st.warning("Event Data Confidence: UNKNOWN. Strict gate blocks ACTIONABLE status.")
t1,t2,t3,t4=st.columns(4)
t1.metric("Entry ref",f'${row["entry_px"]:.2f}'); t2.metric("Stop",f'${row["stop"]:.2f}'); t3.metric("T1",f'${row["t1"]:.2f}'); t4.metric("T2",f'${row["t2"]:.2f}')
st.plotly_chart(chart(g,sel),use_container_width=True)
st.caption(f'Data feed: {client.creds.feed.upper()} • Scan UTC: {res["ts"].strftime("%Y-%m-%d %H:%M:%S")} • Paper orders disabled in V1.')
