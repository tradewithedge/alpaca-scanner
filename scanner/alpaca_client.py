from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

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

    # Latest/snapshot endpoints can use the free 15-minute delayed consolidated feed.
    feed: str = "delayed_sip"

    # Historical SIP is available on Basic when the query end is at least
    # 15 minutes old. Keep it separate from the latest/snapshot feed.
    historical_feed: str = "sip"


class AlpacaClient:
    def __init__(self, creds: AlpacaCredentials, timeout: int = 30):
        self.creds = creds
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "APCA-API-KEY-ID": creds.key_id,
            "APCA-API-SECRET-KEY": creds.secret_key,
            "User-Agent": "alpaca-scanner-v1.1.1",
        })

    def _get(self, url: str, params: Optional[dict] = None, retries: int = 4):
        last_err = None
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                if r.status_code == 429:
                    retry_after = r.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_s = max(float(retry_after), 1.0)
                        except Exception:
                            sleep_s = 1.5 * (attempt + 1)
                    else:
                        sleep_s = 1.5 * (attempt + 1)
                    time.sleep(sleep_s)
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
            payload = self._get(
                url,
                {"symbols": ",".join(batch), "feed": self.creds.feed},
            )
            if isinstance(payload, dict):
                out.update(payload)
        return out

    def _historical_end_utc(self, delay_minutes: int = 20) -> datetime:
        # Free/Basic accounts may query consolidated SIP history when the
        # requested end is at least 15 minutes old. Use a small safety margin.
        return datetime.now(timezone.utc) - timedelta(minutes=delay_minutes)

    def get_previous_daily_bars(
        self,
        symbols: List[str],
        batch_size: int = 100,
    ) -> Dict[str, dict]:
        """Return the last fully completed regular-session daily bar per symbol.

        Uses historical SIP rather than IEX so volume is consolidated across
        U.S. exchanges. This is critical for liquidity gates.
        """
        if not symbols:
            return {}

        now_utc = datetime.now(timezone.utc)
        now_et = now_utc.astimezone(ZoneInfo("America/New_York"))
        midnight_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_utc = midnight_et.astimezone(timezone.utc)

        # Before 00:20 ET, today's midnight is less than 15 minutes old.
        # Using the older of midnight and now-20m stays Basic-plan compatible.
        end_dt = min(midnight_utc, self._historical_end_utc(20))
        start_dt = end_dt - timedelta(days=14)

        start = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        end = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{self.creds.data_base_url.rstrip('/')}/v2/stocks/bars"

        out: Dict[str, dict] = {}
        for batch in self.chunks(symbols, batch_size):
            params = {
                "symbols": ",".join(batch),
                "timeframe": "1Day",
                "start": start,
                "end": end,
                "adjustment": "all",
                "feed": self.creds.historical_feed,
                "sort": "asc",
                "limit": 10000,
            }
            payload = self._get(url, params)
            bars = payload.get("bars", {}) if isinstance(payload, dict) else {}
            for symbol, items in bars.items():
                if not items:
                    continue
                b = items[-1]
                out[symbol] = {
                    "t": b.get("t"),
                    "o": b.get("o"),
                    "h": b.get("h"),
                    "l": b.get("l"),
                    "c": b.get("c"),
                    "v": b.get("v"),
                    "n": b.get("n"),
                    "vw": b.get("vw"),
                }
        return out

    def get_daily_bars(
        self,
        symbols: List[str],
        days: int = 280,
        batch_size: int = 30,
    ) -> pd.DataFrame:
        # Historical SIP is consolidated and is available on Basic as long as
        # `end` is at least 15 minutes old. Do not use IEX history for volume-
        # based screening because IEX represents only one exchange.
        end_dt = self._historical_end_utc(20)
        start_dt = end_dt - timedelta(days=max(days * 2, 420))
        start = start_dt.strftime("%Y-%m-%dT00:00:00Z")
        end = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{self.creds.data_base_url.rstrip('/')}/v2/stocks/bars"

        rows = []
        for batch in self.chunks(symbols, batch_size):
            page_token = None
            while True:
                params = {
                    "symbols": ",".join(batch),
                    "timeframe": "1Day",
                    "start": start,
                    "end": end,
                    "adjustment": "all",
                    "feed": self.creds.historical_feed,
                    "sort": "asc",
                    "limit": 10000,
                }
                if page_token:
                    params["page_token"] = page_token

                payload = self._get(url, params)
                bars = payload.get("bars", {}) if isinstance(payload, dict) else {}

                for symbol, items in bars.items():
                    for b in items:
                        rows.append({
                            "symbol": symbol,
                            "timestamp": b.get("t"),
                            "open": b.get("o"),
                            "high": b.get("h"),
                            "low": b.get("l"),
                            "close": b.get("c"),
                            "volume": b.get("v"),
                            "trade_count": b.get("n"),
                            "vwap": b.get("vw"),
                        })

                page_token = (
                    payload.get("next_page_token")
                    if isinstance(payload, dict)
                    else None
                )
                if not page_token:
                    break

        if not rows:
            return pd.DataFrame(
                columns=[
                    "symbol", "timestamp", "open", "high", "low", "close",
                    "volume",
                ]
            )

        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values(["symbol", "timestamp"])
        return (
            df.groupby("symbol", group_keys=False)
            .tail(days)
            .reset_index(drop=True)
        )
