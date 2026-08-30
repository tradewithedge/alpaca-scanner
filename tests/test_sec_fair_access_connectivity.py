import unittest
from unittest.mock import Mock, patch
import scanner.fundamentals as f


def response(status=200, *, payload=None, text="", reason="OK"):
    r = Mock()
    r.status_code = status
    r.reason = reason
    r.text = text
    if payload is None:
        r.json.side_effect = ValueError("no json")
    else:
        r.json.return_value = payload
    return r


class SecFairAccessConnectivityTests(unittest.TestCase):
    def test_missing_contact_is_not_ready(self):
        cfg = f.build_sec_declared_user_agent()
        self.assertFalse(cfg["ready"])

    def test_contact_builds_declared_ua(self):
        cfg = f.build_sec_declared_user_agent(
            contact_email="owner@example.com",
            organization="TradeWithEdge",
        )
        self.assertTrue(cfg["ready"])
        self.assertIn("owner@example.com", cfg["user_agent"])

    def test_explicit_ua_requires_email(self):
        self.assertFalse(
            f.build_sec_declared_user_agent(
                explicit_user_agent="TradeWithEdge AlpacaScanner"
            )["ready"]
        )
        self.assertTrue(
            f.build_sec_declared_user_agent(
                explicit_user_agent=(
                    "TradeWithEdge AlpacaScanner owner@example.com"
                )
            )["ready"]
        )

    def test_no_declared_email_blocks_official_request_locally(self):
        with self.assertRaises(f.SecAccessError) as ctx:
            f.fetch_sec_companyfacts(1018724, user_agent="")
        self.assertIn("FAIR ACCESS CONFIG", ctx.exception.stage)

    def test_declared_403_classifies_ip_path(self):
        forbidden = response(
            403,
            text="<html><body>Forbidden</body></html>",
            reason="Forbidden",
        )
        with patch("requests.Session.get", return_value=forbidden):
            with self.assertRaises(f.SecAccessError) as ctx:
                f.fetch_sec_companyfacts(
                    1018724,
                    user_agent=(
                        "TradeWithEdge AlpacaScanner owner@example.com"
                    ),
                )
        diagnosis = f.classify_sec_transport_failure(
            stage=ctx.exception.stage,
            status_code=ctx.exception.status_code,
            declaration_ready=True,
        )
        self.assertEqual(
            diagnosis,
            "DECLARED REQUEST BLOCKED — DEPLOYMENT/IP PATH LIKELY",
        )
        self.assertNotIn("<html>", ctx.exception.compact().lower())

    def test_declared_200_passes(self):
        payload = {
            "cik": 1018724,
            "entityName": "AMAZON COM INC",
            "facts": {"us-gaap": {"Revenues": {}}},
        }
        with patch(
            "requests.Session.get",
            return_value=response(200, payload=payload),
        ):
            result = f.fetch_sec_companyfacts(
                1018724,
                user_agent=(
                    "TradeWithEdge AlpacaScanner owner@example.com"
                ),
            )
        self.assertEqual(result["cik"], 1018724)


if __name__ == "__main__":
    unittest.main()
