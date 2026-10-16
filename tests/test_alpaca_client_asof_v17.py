import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd

from scanner.alpaca_client import AlpacaClient, AlpacaCredentials


class HistoricalAsOfBarsTests(unittest.TestCase):
    def setUp(self):
        self.client = AlpacaClient(AlpacaCredentials("test-key", "test-secret"))

    def test_explicit_cutoff_feed_and_pagination(self):
        payloads = [
            {
                "bars": {"AAPL": [
                    {"t": "2024-01-02T00:00:00Z", "o": 1, "h": 2, "l": 1,
                     "c": 2, "v": 10, "n": 3, "vw": 1.5},
                    {"t": "2024-01-03T00:00:00Z", "o": 2, "h": 3, "l": 2,
                     "c": 3, "v": 11, "n": 4, "vw": 2.5},
                ]},
                "next_page_token": "page-2",
            },
            {
                "bars": {"AAPL": [
                    {"t": "2024-01-04T00:00:00Z", "o": 3, "h": 4, "l": 3,
                     "c": 4, "v": 12, "n": 5, "vw": 3.5},
                ]},
                "next_page_token": None,
            },
        ]
        with patch.object(self.client, "_get", side_effect=payloads) as mocked:
            result = self.client.get_daily_bars_asof(
                ["AAPL"], "2024-01-03T23:59:59Z", days=2
            )

        self.assertEqual(len(result), 2)
        self.assertTrue((result["timestamp"] <= pd.Timestamp("2024-01-03T23:59:59Z")).all())
        self.assertEqual(mocked.call_count, 2)
        first_params = mocked.call_args_list[0].args[1]
        second_params = mocked.call_args_list[1].args[1]
        self.assertEqual(first_params["feed"], "sip")
        self.assertEqual(first_params["end"], "2024-01-03T23:59:59Z")
        self.assertEqual(second_params["page_token"], "page-2")

    def test_defensively_filters_future_rows(self):
        with patch.object(self.client, "_get", return_value={
            "bars": {"MSFT": [
                {"t": "2024-01-02T00:00:00Z", "o": 1, "h": 1, "l": 1,
                 "c": 1, "v": 1},
                {"t": "2024-01-04T00:00:00Z", "o": 2, "h": 2, "l": 2,
                 "c": 2, "v": 2},
            ]}
        }):
            result = self.client.get_daily_bars_asof(["MSFT"], "2024-01-03")
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["close"], 1)

    def test_empty_symbols_returns_stable_schema(self):
        result = self.client.get_daily_bars_asof([], "2024-01-03")
        self.assertEqual(
            list(result.columns),
            ["symbol", "timestamp", "open", "high", "low", "close",
             "volume", "trade_count", "vwap"],
        )

    def test_invalid_days_or_batch_size_rejected(self):
        with self.assertRaises(ValueError):
            self.client.get_daily_bars_asof(["AAPL"], "2024-01-03", days=0)
        with self.assertRaises(ValueError):
            self.client.get_daily_bars_asof(["AAPL"], "2024-01-03", batch_size=0)

    def test_asof_timezone_is_normalized_to_utc(self):
        value = self.client._normalise_asof_utc("2024-01-03T01:00:00+01:00")
        self.assertEqual(value, datetime(2024, 1, 3, 0, 0, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
