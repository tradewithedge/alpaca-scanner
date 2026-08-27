from .indicators import latest_snapshot


def score_market_symbol(df):
    s = latest_snapshot(df)
    if not s:
        return {"score": 0, "state": "UNKNOWN"}

    score = 0
    if s.get("close") and s.get("ema20") and s["close"] > s["ema20"]:
        score += 25
    if s.get("close") and s.get("ma50") and s["close"] > s["ma50"]:
        score += 25
    if (s.get("ma20_slope5") or 0) > 0:
        score += 20
    if (s.get("ma50_slope10") or 0) > 0:
        score += 15
    if (s.get("ret20") or 0) > 0:
        score += 15

    state = (
        "RISK-ON"
        if score >= 80
        else "SELECTIVE"
        if score >= 60
        else "MIXED"
        if score >= 40
        else "DEFENSIVE"
    )
    return {"score": score, "state": state, **s}


def aggregate_regime(bars, symbols=("SPY", "QQQ", "IWM")):
    """Return the U.S. market regime based only on fixed broad-market proxies."""
    details, scores = {}, []
    for sym in symbols:
        d = score_market_symbol(bars[bars["symbol"] == sym])
        details[sym] = d
        scores.append(d["score"])

    overall = sum(scores) / len(scores) if scores else 0
    out = _label(overall, details=details)
    out["index_only_score"] = out["score"]
    return out


def with_breadth(regime: dict, cross_section):
    """Attach selected-universe breadth without mutating the market regime.

    V1.1.2 integrity rule:
    - `score`, `label`, and `exposure` remain the fixed U.S. market regime.
    - selected-universe breadth is reported separately.
    - `deployment_score` is the explicit 70/30 market/breadth blend used by
      entry/deployment logic, preserving prior behavior without mislabelling it
      as the market regime.
    """
    out = dict(regime)

    if cross_section is None or cross_section.empty:
        out["breadth"] = {}
        out["deployment_score"] = out.get("score", 0)
        out["deployment_label"] = out.get("label", "UNKNOWN")
        out["deployment_exposure"] = out.get("exposure", "UNKNOWN")
        return out

    total = len(cross_section)
    p20 = 100 * (cross_section["close"] > cross_section["ema20"]).sum() / total
    p50 = 100 * (cross_section["close"] > cross_section["ma50"]).sum() / total
    p200 = (
        100 * (cross_section["close"] > cross_section["ma200"]).sum() / total
        if "ma200" in cross_section
        else 0
    )
    healthy = 100 * (
        (cross_section["close"] > cross_section["ema20"])
        & (cross_section["close"] > cross_section["ma50"])
    ).sum() / total

    breadth_score = 0.35 * p20 + 0.35 * p50 + 0.20 * p200 + 0.10 * healthy
    deployment_score = 0.70 * float(regime.get("score", 0)) + 0.30 * breadth_score
    deployment = _label(deployment_score, details=regime.get("details", {}))

    out["breadth"] = {
        "members": total,
        "above_ema20_pct": round(p20, 1),
        "above_ma50_pct": round(p50, 1),
        "above_ma200_pct": round(p200, 1),
        "above_ema20_and_ma50_pct": round(healthy, 1),
        "breadth_score": round(breadth_score, 1),
    }
    out["deployment_score"] = deployment["score"]
    out["deployment_label"] = deployment["label"]
    out["deployment_exposure"] = deployment["exposure"]
    out["index_only_score"] = regime.get("score", 0)
    return out


def _label(overall, details=None):
    if overall >= 80:
        label, exposure = "BROAD RISK-ON", "NORMAL / ADD ON CONFIRMATION"
    elif overall >= 60:
        label, exposure = "SELECTIVE RISK-ON", "PLAY SLOW — SELECTIVE EXPOSURE"
    elif overall >= 40:
        label, exposure = "MIXED / TRANSITION", "PLAY SLOW & SMALL"
    else:
        label, exposure = "DEFENSIVE", "CAPITAL PRESERVATION / FEW NEW LONGS"

    return {
        "score": round(overall, 1),
        "label": label,
        "exposure": exposure,
        "details": details or {},
    }
