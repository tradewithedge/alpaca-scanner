from .indicators import latest_snapshot

def score_market_symbol(df):
    s = latest_snapshot(df)
    if not s:
        return {"score":0,"state":"UNKNOWN"}
    score = 0
    if s.get("close") and s.get("ema20") and s["close"] > s["ema20"]: score += 25
    if s.get("close") and s.get("ma50") and s["close"] > s["ma50"]: score += 25
    if (s.get("ma20_slope5") or 0) > 0: score += 20
    if (s.get("ma50_slope10") or 0) > 0: score += 15
    if (s.get("ret20") or 0) > 0: score += 15
    state = "RISK-ON" if score>=80 else "SELECTIVE" if score>=60 else "MIXED" if score>=40 else "DEFENSIVE"
    return {"score":score,"state":state,**s}

def aggregate_regime(bars, symbols=("SPY","QQQ","IWM")):
    details, scores = {}, []
    for sym in symbols:
        d = score_market_symbol(bars[bars["symbol"]==sym])
        details[sym] = d
        scores.append(d["score"])
    overall = sum(scores)/len(scores) if scores else 0
    return _label(overall, details=details)

def with_breadth(regime: dict, cross_section):
    if cross_section is None or cross_section.empty:
        regime["breadth"] = {}
        return regime
    total = len(cross_section)
    p20 = 100 * (cross_section["close"] > cross_section["ema20"]).sum() / total
    p50 = 100 * (cross_section["close"] > cross_section["ma50"]).sum() / total
    p200 = 100 * (cross_section["close"] > cross_section["ma200"]).sum() / total if "ma200" in cross_section else 0
    healthy = 100 * ((cross_section["close"] > cross_section["ema20"]) &
                     (cross_section["close"] > cross_section["ma50"])).sum() / total
    breadth_score = 0.35*p20 + 0.35*p50 + 0.20*p200 + 0.10*healthy
    blended = 0.70*regime["score"] + 0.30*breadth_score
    out = _label(blended, details=regime.get("details",{}))
    out["breadth"] = {
        "members": total,
        "above_ema20_pct": round(p20,1),
        "above_ma50_pct": round(p50,1),
        "above_ma200_pct": round(p200,1),
        "above_ema20_and_ma50_pct": round(healthy,1),
        "breadth_score": round(breadth_score,1),
    }
    out["index_only_score"] = regime["score"]
    return out

def _label(overall, details=None):
    if overall>=80:
        label, exposure = "BROAD RISK-ON", "NORMAL / ADD ON CONFIRMATION"
    elif overall>=60:
        label, exposure = "SELECTIVE RISK-ON", "PLAY SLOW — SELECTIVE EXPOSURE"
    elif overall>=40:
        label, exposure = "MIXED / TRANSITION", "PLAY SLOW & SMALL"
    else:
        label, exposure = "DEFENSIVE", "CAPITAL PRESERVATION / FEW NEW LONGS"
    return {"score":round(overall,1),"label":label,"exposure":exposure,"details":details or {}}
