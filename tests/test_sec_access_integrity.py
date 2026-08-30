import unittest
from unittest.mock import patch, Mock

import pandas as pd

import scanner.fundamentals as f


def response(status=200, *, text="", json_payload=None, reason="OK"):
    r = Mock()
    r.status_code = status
    r.reason = reason
    r.text = text
    if json_payload is None:
        r.json.side_effect = ValueError("no json")
    else:
        r.json.return_value = json_payload
    return r


class SecAccessIntegrityTests(unittest.TestCase):
    def test_json_403_falls_back_to_ticker_txt(self):
        json_403 = response(
            403,
            text="Forbidden",
            reason="Forbidden",
        )
        ticker_txt = response(
            200,
            text="amzn\t1018724\nmsft\t789019\n",
        )

        with patch("requests.Session.get", side_effect=[json_403, ticker_txt]):
            identity = f.resolve_sec_identity(
                "AMZN",
                user_agent="TradeWithEdge Test test@example.com",
            )

        self.assertEqual(identity["cik"], 1018724)
        self.assertEqual(identity["identity_source"], "SEC ticker.txt")
        self.assertEqual(identity["identity_access_status"], "PASS")
        self.assertIn("HTTP 403", identity["identity_diagnostics"])

    def test_json_and_txt_failure_can_fall_back_to_exchange_json(self):
        bad1 = response(403, text="Forbidden", reason="Forbidden")
        bad2 = response(403, text="Forbidden", reason="Forbidden")
        exchange = response(
            200,
            json_payload={
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [[1018724, "AMAZON COM INC", "AMZN", "Nasdaq"]],
            },
        )

        with patch(
            "requests.Session.get",
            side_effect=[bad1, bad2, exchange],
        ):
            identity = f.resolve_sec_identity(
                "AMZN",
                user_agent="TradeWithEdge Test test@example.com",
            )

        self.assertEqual(identity["cik"], 1018724)
        self.assertEqual(
            identity["identity_source"],
            "SEC company_tickers_exchange.json",
        )

    def test_companyfacts_403_is_structured(self):
        forbidden = response(
            403,
            text="Forbidden",
            reason="Forbidden",
        )
        with patch("requests.Session.get", return_value=forbidden):
            with self.assertRaises(f.SecAccessError) as ctx:
                f.fetch_sec_companyfacts(
                    1018724,
                    user_agent="TradeWithEdge Test test@example.com",
                )
        self.assertEqual(ctx.exception.stage, "SEC COMPANYFACTS")
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertFalse(ctx.exception.retryable)

    def test_ticker_absent_is_not_misreported_as_transport_failure(self):
        empty_for_target = {
            "0": {
                "ticker": "MSFT",
                "cik_str": 789019,
                "title": "MICROSOFT CORP",
            }
        }
        txt = "msft\t789019\n"
        exchange = {
            "fields": ["cik", "name", "ticker", "exchange"],
            "data": [[789019, "MICROSOFT CORP", "MSFT", "Nasdaq"]],
        }

        with patch(
            "requests.Session.get",
            side_effect=[
                response(200, json_payload=empty_for_target),
                response(200, text=txt),
                response(200, json_payload=exchange),
            ],
        ):
            with self.assertRaises(f.SecIdentityNotFound):
                f.resolve_sec_identity(
                    "ZZZZ",
                    user_agent="TradeWithEdge Test test@example.com",
                )

    def test_unavailable_snapshot_separates_access_failure(self):
        snap = f.unavailable_snapshot(
            "AMZN",
            "SEC IDENTITY company_tickers.json: HTTP 403",
            sec_access_status="SEC IDENTITY ACCESS FAILED",
            identity_access_status="FAILED",
            companyfacts_access_status="NOT ATTEMPTED",
        )
        self.assertEqual(
            snap["sec_access_status"],
            "SEC IDENTITY ACCESS FAILED",
        )
        self.assertEqual(snap["fundamental_confidence"], "UNKNOWN")
        self.assertTrue(pd.isna(snap["fundamental_score"]))


if __name__ == "__main__":
    unittest.main()
