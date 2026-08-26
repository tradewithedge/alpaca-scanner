from .indicators import latest_snapshot

def score_market_symbol(df):
    s = latest_snapshot(df)
    if not s: return {"score":0,"state":"UNKNOWN"}
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
    if overall>=80: label, exposure = "BROAD RISK-ON", "NORMAL / ADD ON CONFIRMATION"
    elif overall>=60: label, exposure = "SELECTIVE RISK-ON", "PLAY SLOW — SELECTIVE EXPOSURE"
    elif overall>=40: label, exposure = "MIXED / TRANSITION", "PLAY SLOW & SMALL"
    else: label, exposure = "DEFENSIVE", "CAPITAL PRESERVATION / FEW NEW LONGS"
    return {"score":round(overall,1),"label":label,"exposure":exposure,"details":details}
