from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable
import pandas as pd
import requests
from io import StringIO

@dataclass
class UniverseResult:
    name: str
    symbols: Optional[list[str]]
    source: str
    source_type: str
    note: str = ""

UNIVERSE_OPTIONS = [
    "All U.S. Tradable / Liquid",
    "S&P 500",
    "NASDAQ-100",
    "Russell 1000 (IWB proxy)",
    "Russell 2000 (IWM proxy)",
    "S&P MidCap 400",
    "S&P SmallCap 600",
    "Dow Jones 30",
]

def _norm_symbol(x: str) -> str:
    return str(x).strip().upper().replace(".", "-")

def _table_symbols(url: str, candidate_cols: Iterable[str]) -> list[str]:
    tables = pd.read_html(url)
    for t in tables:
        for col in candidate_cols:
            if col in t.columns:
                vals = [_norm_symbol(x) for x in t[col].dropna().tolist()]
                vals = [x for x in vals if x and x not in {"NAN", "NONE"}]
                if len(vals) >= 20:
                    return sorted(set(vals))
    raise RuntimeError(f"Could not find symbol column at {url}")

def _ishares_holdings(url: str) -> list[str]:
    r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    lines = r.text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("Ticker,") or line.startswith('"Ticker"'):
            start = i
            break
    if start is None:
        raise RuntimeError("Ticker header not found in iShares holdings CSV")
    df = pd.read_csv(StringIO("\n".join(lines[start:])))
    if "Ticker" not in df.columns:
        raise RuntimeError("Ticker column not found in iShares holdings")
    vals = [_norm_symbol(x) for x in df["Ticker"].dropna().tolist()]
    return sorted(set(x for x in vals if x and x not in {"-", "NAN", "CASH_USD"}))

def fetch_universe(name: str) -> UniverseResult:
    if name == "All U.S. Tradable / Liquid":
        return UniverseResult(name, None, "Alpaca active U.S. equities", "ALPACA",
                              "Universe is defined by active/tradable Alpaca U.S. equities, then quality filters.")
    if name == "S&P 500":
        syms = _table_symbols("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", ["Symbol"])
        return UniverseResult(name, syms, "Wikipedia constituent table", "PUBLIC_TABLE",
                              "Refreshed at scan time; may lag official index notices.")
    if name == "NASDAQ-100":
        syms = _table_symbols("https://en.wikipedia.org/wiki/Nasdaq-100", ["Ticker", "Symbol"])
        return UniverseResult(name, syms, "Wikipedia constituent table", "PUBLIC_TABLE",
                              "Refreshed at scan time.")
    if name == "S&P MidCap 400":
        syms = _table_symbols("https://en.wikipedia.org/wiki/List_of_S%26P_400_companies", ["Symbol", "Ticker"])
        return UniverseResult(name, syms, "Wikipedia constituent table", "PUBLIC_TABLE",
                              "Refreshed at scan time.")
    if name == "S&P SmallCap 600":
        syms = _table_symbols("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies", ["Symbol", "Ticker"])
        return UniverseResult(name, syms, "Wikipedia constituent table", "PUBLIC_TABLE",
                              "Refreshed at scan time.")
    if name == "Dow Jones 30":
        syms = _table_symbols("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average", ["Symbol", "Ticker"])
        return UniverseResult(name, syms, "Wikipedia constituent table", "PUBLIC_TABLE",
                              "Refreshed at scan time.")
    if name == "Russell 2000 (IWM proxy)":
        url = ("https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/"
               "1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund")
        syms = _ishares_holdings(url)
        return UniverseResult(name, syms, "iShares IWM holdings", "ETF_PROXY",
                              "Practical Russell 2000 proxy; not exact licensed index membership.")
    if name == "Russell 1000 (IWB proxy)":
        url = ("https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/"
               "1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund")
        syms = _ishares_holdings(url)
        return UniverseResult(name, syms, "iShares IWB holdings", "ETF_PROXY",
                              "Practical Russell 1000 proxy; not exact licensed index membership.")
    raise ValueError(f"Unsupported universe: {name}")
