from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import pandas as pd
import requests

class AlpacaError(RuntimeError):
    pass

@dataclass
class AlpacaCredentials:
    key_id: str
    secret_key: str
    data_base_url: str = "https://data.alpaca.markets"
    paper_base_url: str = "https://paper-api.alpaca.markets"
    feed: str = "iex"

class AlpacaClient:
    def __init__(self, creds: AlpacaCredentials, timeout: int = 30):
        self.creds = creds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "APCA-API-KEY-ID": creds.key_id,
            "APCA-API-SECRET-KEY": creds.secret_key,
            "User-Agent": "alpaca-scanner-v1.1",
        })

    def _get(self, url: str, params: Optional[dict] = None, retries: int = 3):
        last_err = None
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                if r.status_code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as exc:
                last_err = exc
                time.sleep(0.5 * (attempt + 1))
        raise AlpacaError(f"Alpaca request failed: {last_err}")

    def get_assets(self) -> List[dict]:
        url = f"{self.creds.paper_base_url.rstrip('/')}/v2/assets"
        data = self._get(url, {"status": "active", "asset_class": "us_equity"})
        if not isinstance(data, list):
            raise AlpacaError("Unexpected assets response")
        return data

    @staticmethod
    def chunks(items: List[str], n: int):
        for i in range(0, len(items), n):
            yield items[i:i+n]

    def get_snapshots(self, symbols: List[str], batch_size: int = 100) -> Dict[str, dict]:
        out = {}
        url = f"{self.creds.data_base_url.rstrip('/')}/v2/stocks/snapshots"
        for batch in self.chunks(symbols, batch_size):
            payload = self._get(url, {"symbols": ",".join(batch), "feed": self.creds.feed})
            if isinstance(payload, dict):
                out.update(payload)
        return out

    def get_daily_bars(self, symbols: List[str], days: int = 280, batch_size: int = 40) -> pd.DataFrame:
        start = (datetime.now(timezone.utc) - timedelta(days=max(days * 2, 420))).strftime("%Y-%m-%dT00:00:00Z")
        end = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59Z")
        url = f"{self.creds.data_base_url.rstrip('/')}/v2/stocks/bars"
        rows = []
        for batch in self.chunks(symbols, batch_size):
            page_token = None
            while True:
                params = {
                    "symbols": ",".join(batch), "timeframe": "1Day",
                    "start": start, "end": end, "adjustment": "all",
                    "feed": self.creds.feed, "sort": "asc", "limit": 10000,
                }
                if page_token:
                    params["page_token"] = page_token
                payload = self._get(url, params)
                bars = payload.get("bars", {}) if isinstance(payload, dict) else {}
                for symbol, items in bars.items():
                    for b in items:
                        rows.append({
                            "symbol": symbol, "timestamp": b.get("t"),
                            "open": b.get("o"), "high": b.get("h"), "low": b.get("l"),
                            "close": b.get("c"), "volume": b.get("v"),
                            "trade_count": b.get("n"), "vwap": b.get("vw"),
                        })
                page_token = payload.get("next_page_token") if isinstance(payload, dict) else None
                if not page_token:
                    break
        if not rows:
            return pd.DataFrame(columns=["symbol","timestamp","open","high","low","close","volume"])
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values(["symbol","timestamp"])
        return df.groupby("symbol", group_keys=False).tail(days).reset_index(drop=True)
