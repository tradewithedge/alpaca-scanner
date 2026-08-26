import numpy as np
import pandas as pd
from .indicators import add_indicators
from .config import ScannerConfig

def _pct_rank(s): return s.rank(pct=True)*100

def build_cross_section(bars, spy_ret20, spy_ret50):
    rows=[]
    for symbol,g in bars.groupby("symbol"):
        g=add_indicators(g)
        if len(g)<55: continue
        r=g.iloc[-1]
        rows.append({k:r.get(k) for k in [
            "close","ema8","ema20","ma50","atr14","ret5","ret20","ret50","vol_ratio",
            "range5","range20","atr5","atr20","high20_prev","low10","ma20_slope5","ma50_slope10"
        ]} | {"symbol":symbol,"bars":len(g),"last_ts":r["timestamp"]})
    x=pd.DataFrame(rows)
    if x.empty: return x
    x["rs20"]=x["ret20"]-(spy_ret20 or 0)
    x["rs50"]=x["ret50"]-(spy_ret50 or 0)
    x["rs20_pct"]=_pct_rank(x["rs20"].fillna(-999))
    x["rs50_pct"]=_pct_rank(x["rs50"].fillna(-999))
    x["rs_score"]=0.6*x["rs20_pct"]+0.4*x["rs50_pct"]
    x["ext_ema8_pct"]=100*(x["close"]/x["ema8"]-1)
    x["ext_ema20_pct"]=100*(x["close"]/x["ema20"]-1)
    x["ext_atr"]=(x["close"]-x["ema20"])/x["atr14"].replace(0,np.nan)
    return x

def detect_setup(r):
    above20 = pd.notna(r["ema20"]) and r["close"]>r["ema20"]
    above50 = pd.notna(r["ma50"]) and r["close"]>r["ma50"]
    near20 = pd.notna(r["ext_ema20_pct"]) and -1.5<=r["ext_ema20_pct"]<=3.5
    contraction = pd.notna(r["atr5"]) and pd.notna(r["atr20"]) and r["atr20"]>0 and r["atr5"]/r["atr20"]<0.78 and pd.notna(r["range5"]) and pd.notna(r["range20"]) and r["range20"]>0 and r["range5"]/r["range20"]<0.78
    breakout = pd.notna(r["high20_prev"]) and r["close"]>r["high20_prev"]*1.001
    volume_ok = pd.notna(r["vol_ratio"]) and r["vol_ratio"]>=1.2
    if breakout and volume_ok and above20 and above50: return "CONFIRMED BREAKOUT",95
    if breakout and not volume_ok: return "LOW-CONFIDENCE BREAKOUT",58
    if near20 and above50 and (r.get("ma20_slope5") or 0)>0: return "EMA20 PULLBACK",90
    if contraction and above20 and above50: return "VCP / TIGHTENING",88
    if above20 and above50 and pd.notna(r["range20"]) and r["range20"]<0.10: return "TIGHT BASE / DEVELOPING",78
    if not above20 and above50: return "MA20 REPAIR WINDOW",50
    if not above50: return "BROKEN / BELOW MA50",20
    return "TRENDING / NO CLEAN SETUP",55

def score_universe(x, regime_score, cfg:ScannerConfig):
    out=[]
    for _,r in x.iterrows():
        setup, setup_score = detect_setup(r)
        trend=0
        if r["close"]>r["ema8"]: trend+=8
        if r["close"]>r["ema20"]: trend+=12
        if pd.notna(r["ma50"]) and r["close"]>r["ma50"]: trend+=10
        if (r.get("ma20_slope5") or 0)>0: trend+=8
        if (r.get("ma50_slope10") or 0)>0: trend+=7
        quality=min(100, trend + min(max((r.get("rs_score") or 0)*0.30,0),30) + setup_score*0.20 + 5)
        entry=0.55*setup_score
        ext20, ext8, extatr = r.get("ext_ema20_pct"), r.get("ext_ema8_pct"), r.get("ext_atr")
        if pd.notna(ext20):
            entry += 22 if -1.5<=ext20<=3.0 else 12 if 3.0<ext20<=6.0 else 4 if ext20<-1.5 else 0
        if pd.notna(r.get("vol_ratio")):
            if setup=="CONFIRMED BREAKOUT" and r["vol_ratio"]>=1.2: entry+=12
            elif setup in ("EMA20 PULLBACK","VCP / TIGHTENING") and r["vol_ratio"]<=1.1: entry+=8
        entry += 8 if regime_score>=60 else -10 if regime_score<40 else 0
        entry=max(0,min(100,entry))
        chase_reasons=[]
        if pd.notna(ext8) and ext8>cfg.max_ext_ema8_pct: chase_reasons.append(f"{ext8:.1f}% above EMA8")
        if pd.notna(ext20) and ext20>cfg.max_ext_ema20_pct: chase_reasons.append(f"{ext20:.1f}% above EMA20")
        if pd.notna(extatr) and extatr>cfg.max_ext_atr: chase_reasons.append(f"{extatr:.1f} ATR above EMA20")
        chase=bool(chase_reasons)
        event_confidence="UNKNOWN"
        if chase:
            bucket="A-QUALITY — WAIT" if quality>=cfg.min_quality_wait else "WAIT"; decision="WAIT — EXTENDED"
        elif quality>=cfg.min_quality_actionable and entry>=cfg.min_entry_actionable and regime_score>=40:
            if cfg.strict_event_gate:
                bucket="A-QUALITY — WAIT"; decision="WAIT — EVENT DATE UNVERIFIED"
            else:
                bucket="ACTIONABLE NOW"; decision="ACTIONABLE"
        elif quality>=cfg.min_quality_wait:
            bucket="A-QUALITY — WAIT"; decision="WAIT"
        elif quality>=cfg.min_quality_developing:
            bucket="DEVELOPING"; decision="DEVELOPING"
        else:
            bucket="AVOID / BROKEN"; decision="AVOID"
        px=float(r["close"]); atr=float(r["atr14"]) if pd.notna(r["atr14"]) and r["atr14"]>0 else px*0.03
        supp=[v for v in [r.get("ema20"),r.get("low10")] if pd.notna(v)]
        support=min(supp) if supp else px-atr
        stop=max(0.01,float(support)-0.25*atr); risk=max(px-stop,0.01)
        d=r.to_dict()
        d.update({"setup":setup,"quality_score":round(quality,1),"entry_score":round(entry,1),
                  "bucket":bucket,"decision":decision,"chase_reasons":"; ".join(chase_reasons),
                  "event_confidence":event_confidence,"entry_px":round(px,2),"stop":round(stop,2),
                  "t1":round(px+1.5*risk,2),"t2":round(px+2.5*risk,2)})
        out.append(d)
    if not out: return pd.DataFrame()
    z=pd.DataFrame(out)
    order={"ACTIONABLE NOW":0,"A-QUALITY — WAIT":1,"DEVELOPING":2,"WAIT":3,"AVOID / BROKEN":4}
    z["_o"]=z["bucket"].map(order).fillna(9)
    return z.sort_values(["_o","quality_score","entry_score","rs_score"],ascending=[True,False,False,False]).drop(columns="_o")
