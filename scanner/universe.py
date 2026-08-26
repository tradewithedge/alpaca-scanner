from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Iterable, Optional
from urllib.parse import urlparse, unquote

import pandas as pd
import requests


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


_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0 Safari/537.36 ALPACA-Scanner/1.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _norm_symbol(x: str) -> str:
    return str(x).strip().upper().replace(".", "-")


def _extract_symbols_from_tables(html: str, candidate_cols: Iterable[str]) -> list[str]:
    tables = pd.read_html(StringIO(html))
    for table in tables:
        # Flatten a possible MultiIndex header.
        if isinstance(table.columns, pd.MultiIndex):
            table.columns = [
                " ".join(str(v) for v in col if str(v) != "nan").strip()
                for col in table.columns
            ]

        normalized = {str(c).strip().lower(): c for c in table.columns}

        for wanted in candidate_cols:
            target = None
            wanted_l = wanted.strip().lower()

            if wanted_l in normalized:
                target = normalized[wanted_l]
            else:
                # Allow headers such as "Symbol Ticker".
                for low_name, original in normalized.items():
                    if wanted_l in low_name:
                        target = original
                        break

            if target is None:
                continue

            vals = [_norm_symbol(x) for x in table[target].dropna().tolist()]
            vals = [
                x for x in vals
                if x and x not in {"NAN", "NONE", "-", "—"} and len(x) <= 10
            ]
            if len(vals) >= 20:
                return sorted(set(vals))

    raise RuntimeError("Could not find a valid symbol column in downloaded tables")


def _wikipedia_page_title(url: str) -> str:
    path = unquote(urlparse(url).path)
    marker = "/wiki/"
    if marker not in path:
        raise RuntimeError(f"Not a Wikipedia article URL: {url}")
    return path.split(marker, 1)[1].replace("_", " ")


def _wikipedia_html_via_api(article_url: str) -> str:
    """Use MediaWiki API instead of direct page scraping.

    This is intentionally a fallback because Streamlit Cloud / pandas.read_html
    can receive HTTP 403 responses from direct Wikipedia page requests.
    """
    title = _wikipedia_page_title(article_url)
    api = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": 2,
        "redirects": 1,
    }
    r = requests.get(api, params=params, headers=_BROWSER_HEADERS, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if "error" in payload:
        raise RuntimeError(f"MediaWiki API error: {payload['error']}")
    html = (payload.get("parse") or {}).get("text")
    if not html:
        raise RuntimeError("MediaWiki API returned no page HTML")
    return html


def _table_symbols(url: str, candidate_cols: Iterable[str]) -> list[str]:
    """Robust table reader with Streamlit-safe fallbacks.

    1. Browser-like requests GET (instead of pandas fetching the URL itself).
    2. For Wikipedia, MediaWiki API fallback.
    """
    errors = []

    try:
        r = requests.get(url, timeout=30, headers=_BROWSER_HEADERS)
        r.raise_for_status()
        return _extract_symbols_from_tables(r.text, candidate_cols)
    except Exception as exc:
        errors.append(f"direct GET: {exc}")

    if "wikipedia.org" in url.lower():
        try:
            html = _wikipedia_html_via_api(url)
            return _extract_symbols_from_tables(html, candidate_cols)
        except Exception as exc:
            errors.append(f"MediaWiki API: {exc}")

    raise RuntimeError(
        f"Could not load index constituents from {url}. "
        + " | ".join(errors)
    )


def _csv_symbols(url: str, candidate_cols: Iterable[str]) -> list[str]:
    r = requests.get(url, timeout=30, headers=_BROWSER_HEADERS)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))

    normalized = {str(c).strip().lower(): c for c in df.columns}
    for wanted in candidate_cols:
        wanted_l = wanted.strip().lower()
        target = normalized.get(wanted_l)
        if target is None:
            for low_name, original in normalized.items():
                if wanted_l in low_name:
                    target = original
                    break
        if target is None:
            continue

        vals = [_norm_symbol(x) for x in df[target].dropna().tolist()]
        vals = [x for x in vals if x and x not in {"NAN", "NONE", "-", "—"}]
        if len(vals) >= 20:
            return sorted(set(vals))

    raise RuntimeError(f"Could not find symbol column in CSV: {url}")


def _first_success(loaders):
    errors = []
    for description, fn in loaders:
        try:
            symbols = fn()
            if len(symbols) < 20:
                raise RuntimeError(f"Only {len(symbols)} symbols returned")
            return symbols, description
        except Exception as exc:
            errors.append(f"{description}: {exc}")
    raise RuntimeError("All universe sources failed. " + " | ".join(errors))


def _ishares_holdings(url: str) -> list[str]:
    r = requests.get(url, timeout=30, headers=_BROWSER_HEADERS)
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
    return sorted(
        set(x for x in vals if x and x not in {"-", "NAN", "CASH_USD"})
    )


def fetch_universe(name: str) -> UniverseResult:
    if name == "All U.S. Tradable / Liquid":
        return UniverseResult(
            name,
            None,
            "Alpaca active U.S. equities",
            "ALPACA",
            "Universe is defined by active/tradable Alpaca U.S. equities, then quality filters.",
        )

    if name == "S&P 500":
        syms, source = _first_success([
            (
                "GitHub-hosted current constituent CSV",
                lambda: _csv_symbols(
                    "https://yfiua.github.io/index-constituents/constituents-sp500.csv",
                    ["symbol", "ticker"],
                ),
            ),
            (
                "Wikipedia / MediaWiki",
                lambda: _table_symbols(
                    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                    ["Symbol", "Ticker"],
                ),
            ),
        ])
        return UniverseResult(
            name, syms, source, "PUBLIC_TABLE",
            "Uses a GitHub-hosted current snapshot first, with MediaWiki fallback. "
            "Membership can lag official S&P notices."
        )

    if name == "NASDAQ-100":
        syms, source = _first_success([
            (
                "GitHub-hosted current constituent CSV",
                lambda: _csv_symbols(
                    "https://yfiua.github.io/index-constituents/constituents-nasdaq100.csv",
                    ["symbol", "ticker"],
                ),
            ),
            (
                "Wikipedia / MediaWiki",
                lambda: _table_symbols(
                    "https://en.wikipedia.org/wiki/Nasdaq-100",
                    ["Ticker", "Symbol"],
                ),
            ),
        ])
        return UniverseResult(
            name, syms, source, "PUBLIC_TABLE",
            "Uses a GitHub-hosted current snapshot first, with MediaWiki fallback."
        )

    if name == "S&P MidCap 400":
        syms = _table_symbols(
            "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
            ["Symbol", "Ticker"],
        )
        return UniverseResult(
            name, syms, "Wikipedia via browser/MediaWiki fallback", "PUBLIC_TABLE",
            "Refreshed at scan time; may lag official S&P notices."
        )

    if name == "S&P SmallCap 600":
        syms = _table_symbols(
            "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies",
            ["Symbol", "Ticker"],
        )
        return UniverseResult(
            name, syms, "Wikipedia via browser/MediaWiki fallback", "PUBLIC_TABLE",
            "Refreshed at scan time; may lag official S&P notices."
        )

    if name == "Dow Jones 30":
        syms, source = _first_success([
            (
                "GitHub-hosted current constituent CSV",
                lambda: _csv_symbols(
                    "https://yfiua.github.io/index-constituents/constituents-dowjones.csv",
                    ["symbol", "ticker"],
                ),
            ),
            (
                "Wikipedia / MediaWiki",
                lambda: _table_symbols(
                    "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
                    ["Symbol", "Ticker"],
                ),
            ),
        ])
        return UniverseResult(
            name, syms, source, "PUBLIC_TABLE",
            "Uses a GitHub-hosted current snapshot first, with MediaWiki fallback."
        )

    if name == "Russell 2000 (IWM proxy)":
        url = (
            "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/"
            "1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund"
        )
        syms = _ishares_holdings(url)
        return UniverseResult(
            name, syms, "iShares IWM holdings", "ETF_PROXY",
            "Practical Russell 2000 proxy; not exact licensed index membership."
        )

    if name == "Russell 1000 (IWB proxy)":
        url = (
            "https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/"
            "1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund"
        )
        syms = _ishares_holdings(url)
        return UniverseResult(
            name, syms, "iShares IWB holdings", "ETF_PROXY",
            "Practical Russell 1000 proxy; not exact licensed index membership."
        )

    raise ValueError(f"Unsupported universe: {name}")
