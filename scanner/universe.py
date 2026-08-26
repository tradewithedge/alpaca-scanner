from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Iterable, Optional
from urllib.parse import unquote, urlparse

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
    "Connection": "keep-alive",
}


def _norm_symbol(x: str) -> str:
    return str(x).strip().upper().replace(".", "-")


def _clean_symbols(values: Iterable[object]) -> list[str]:
    bad = {
        "", "NAN", "NONE", "-", "—", "USD", "CASH_USD",
        "BLK CSH FND TREASURY SL AGENCY",
    }
    vals = [_norm_symbol(x) for x in values]
    vals = [x for x in vals if x not in bad and 1 <= len(x) <= 10]
    return sorted(set(vals))


def _validate_count(
    universe_name: str,
    symbols: list[str],
    minimum: int,
    maximum: Optional[int] = None,
) -> list[str]:
    n = len(symbols)
    if n < minimum:
        raise RuntimeError(
            f"{universe_name} source returned only {n} symbols; "
            f"expected at least {minimum}. Source may be blocked, truncated, or changed."
        )
    if maximum is not None and n > maximum:
        raise RuntimeError(
            f"{universe_name} source returned {n} symbols; "
            f"expected at most {maximum}. Source format may have changed."
        )
    return symbols


def _extract_symbols_from_tables(
    html: str,
    candidate_cols: Iterable[str],
) -> list[str]:
    tables = pd.read_html(StringIO(html))

    for table in tables:
        if isinstance(table.columns, pd.MultiIndex):
            table.columns = [
                " ".join(str(v) for v in col if str(v) != "nan").strip()
                for col in table.columns
            ]

        normalized = {str(c).strip().lower(): c for c in table.columns}

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

            vals = _clean_symbols(table[target].dropna().tolist())
            if len(vals) >= 20:
                return vals

    raise RuntimeError("Could not find a valid symbol column in downloaded tables")


def _wikipedia_page_title(url: str) -> str:
    path = unquote(urlparse(url).path)
    marker = "/wiki/"
    if marker not in path:
        raise RuntimeError(f"Not a Wikipedia article URL: {url}")
    return path.split(marker, 1)[1].replace("_", " ")


def _wikipedia_html_via_api(article_url: str) -> str:
    """Fetch a Wikipedia article through the MediaWiki API.

    This avoids relying only on direct article HTML, which can return HTTP 403
    from some cloud-hosted environments.
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
    """Read an HTML constituent table with a Wikipedia API fallback."""
    errors: list[str] = []

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
        f"Could not load index constituents from {url}. " + " | ".join(errors)
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

        vals = _clean_symbols(df[target].dropna().tolist())
        if len(vals) >= 20:
            return vals

    raise RuntimeError(f"Could not find symbol column in CSV: {url}")


def _first_success(
    loaders,
    universe_name: str,
    minimum: int,
    maximum: Optional[int] = None,
):
    errors: list[str] = []

    for description, fn in loaders:
        try:
            symbols = fn()
            symbols = _validate_count(
                universe_name,
                symbols,
                minimum=minimum,
                maximum=maximum,
            )
            return symbols, description
        except Exception as exc:
            errors.append(f"{description}: {exc}")

    raise RuntimeError(
        f"All sources failed for {universe_name}. " + " | ".join(errors)
    )


def _ishares_holdings(
    product_page_url: str,
    csv_url: str,
    universe_name: str,
    minimum: int,
    maximum: Optional[int] = None,
) -> list[str]:
    """Download current iShares holdings with a browser-like session.

    iShares retired/changed older AJAX download URLs. The current product pages
    expose stable `latest-holdings.csv` links. A warm-up product-page request
    also gives the session any cookies expected by the download endpoint.
    """
    session = requests.Session()
    session.headers.update(_BROWSER_HEADERS)

    # Warm up the session. Failure here is non-fatal; the CSV may still work.
    try:
        session.get(product_page_url, timeout=20)
    except Exception:
        pass

    csv_headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/csv,text/plain,*/*",
        "Referer": product_page_url,
    }

    r = session.get(csv_url, timeout=45, headers=csv_headers)
    r.raise_for_status()

    lines = r.text.splitlines()
    start = None
    for i, line in enumerate(lines):
        stripped = line.lstrip("\ufeff").strip()
        if stripped.startswith("Ticker,") or stripped.startswith('"Ticker"'):
            start = i
            break

    if start is None:
        raise RuntimeError(
            f"Ticker header not found in iShares holdings CSV for {universe_name}"
        )

    df = pd.read_csv(StringIO("\n".join(lines[start:])))
    if "Ticker" not in df.columns:
        raise RuntimeError(
            f"Ticker column not found in iShares holdings for {universe_name}"
        )

    # Keep actual equity holdings only. This removes cash funds, futures,
    # collateral and other non-stock rows that can appear in ETF holdings.
    if "Type" in df.columns:
        type_mask = df["Type"].astype(str).str.upper().eq("EQUITY")
        if type_mask.any():
            df = df[type_mask]
    elif "Asset Class" in df.columns:
        class_mask = df["Asset Class"].astype(str).str.upper().eq("EQUITY")
        if class_mask.any():
            df = df[class_mask]

    symbols = _clean_symbols(df["Ticker"].dropna().tolist())
    return _validate_count(
        universe_name,
        symbols,
        minimum=minimum,
        maximum=maximum,
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
        syms, source = _first_success(
            [
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
            ],
            universe_name=name,
            minimum=480,
            maximum=520,
        )
        return UniverseResult(
            name,
            syms,
            source,
            "PUBLIC_TABLE",
            "Current public constituent source with validated membership count; "
            "may lag official S&P notices.",
        )

    if name == "NASDAQ-100":
        syms, source = _first_success(
            [
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
            ],
            universe_name=name,
            minimum=95,
            maximum=110,
        )
        return UniverseResult(
            name,
            syms,
            source,
            "PUBLIC_TABLE",
            "Current public constituent source with validated membership count.",
        )

    if name == "S&P MidCap 400":
        syms = _validate_count(
            name,
            _table_symbols(
                "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
                ["Symbol", "Ticker"],
            ),
            minimum=380,
            maximum=420,
        )
        return UniverseResult(
            name,
            syms,
            "Wikipedia via browser/MediaWiki fallback",
            "PUBLIC_TABLE",
            "Refreshed at scan time with validated membership count; "
            "may lag official S&P notices.",
        )

    if name == "S&P SmallCap 600":
        ijr_page = (
            "https://www.ishares.com/us/products/239774/"
            "ishares-core-sp-smallcap-etf"
        )
        ijr_csv = (
            "https://www.ishares.com/us/products/239774/"
            "ishares-core-s-p-small-cap-etf/latest-holdings.csv"
        )

        syms, source = _first_success(
            [
                (
                    "Wikipedia / MediaWiki exact constituent table",
                    lambda: _table_symbols(
                        "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies",
                        ["Symbol", "Ticker"],
                    ),
                ),
                (
                    "iShares IJR holdings fallback (S&P SmallCap 600 tracker)",
                    lambda: _ishares_holdings(
                        ijr_page,
                        ijr_csv,
                        name,
                        minimum=580,
                        maximum=700,
                    ),
                ),
            ],
            universe_name=name,
            minimum=580,
            maximum=700,
        )

        source_type = (
            "ETF_PROXY" if source.startswith("iShares IJR") else "PUBLIC_TABLE"
        )
        note = (
            "Exact public table is preferred. If it is unavailable, IJR holdings "
            "are used as a clearly identified S&P SmallCap 600 tracking proxy. "
            "No silent substitution to All U.S. is allowed."
        )
        return UniverseResult(name, syms, source, source_type, note)

    if name == "Dow Jones 30":
        syms, source = _first_success(
            [
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
            ],
            universe_name=name,
            minimum=28,
            maximum=32,
        )
        return UniverseResult(
            name,
            syms,
            source,
            "PUBLIC_TABLE",
            "Current public constituent source with validated membership count.",
        )

    if name == "Russell 2000 (IWM proxy)":
        page = "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf"
        csv = page + "/latest-holdings.csv"
        syms = _ishares_holdings(
            page,
            csv,
            name,
            minimum=1800,
            maximum=2100,
        )
        return UniverseResult(
            name,
            syms,
            "iShares IWM current latest-holdings.csv",
            "ETF_PROXY",
            "Practical Russell 2000 proxy using current IWM equity holdings; "
            "not exact licensed Russell index membership.",
        )

    if name == "Russell 1000 (IWB proxy)":
        page = "https://www.ishares.com/us/products/239707/ishares-russell-1000-etf"
        csv = page + "/latest-holdings.csv"
        syms = _ishares_holdings(
            page,
            csv,
            name,
            minimum=900,
            maximum=1100,
        )
        return UniverseResult(
            name,
            syms,
            "iShares IWB current latest-holdings.csv",
            "ETF_PROXY",
            "Practical Russell 1000 proxy using current IWB equity holdings; "
            "not exact licensed Russell index membership.",
        )

    raise ValueError(f"Unsupported universe: {name}")
