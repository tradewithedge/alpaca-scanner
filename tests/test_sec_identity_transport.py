import unittest
from unittest.mock import Mock, patch

import scanner.fundamentals as f


def resp(status=200, *, json_payload=None, text="", reason="OK"):
    r = Mock()
    r.status_code = status
    r.reason = reason
    r.text = text
    if json_payload is None:
        r.json.side_effect = ValueError("no JSON")
    else:
        r.json.return_value = json_payload
    return r


class SecIdentityTransportBypassTests(unittest.TestCase):
    def test_primary_sec_403_goes_directly_to_pinned_mirror(self):
        official_403 = resp(
            403,
            text="Forbidden",
            reason="Forbidden",
        )
        mirror_payload = {
            "1018724": "AMZN",
            "789019": "MSFT",
        }
        mirror_ok = resp(200, json_payload=mirror_payload)

        with patch(
            "requests.Session.get",
            return_value=official_403,
        ), patch(
            "requests.get",
            return_value=mirror_ok,
        ):
            identity = f.resolve_sec_identity(
                "AMZN",
                user_agent="TradeWithEdge Test test@example.com",
            )

        self.assertEqual(identity["cik"], 1018724)
        self.assertEqual(
            identity["identity_source"],
            f.SEC_IDENTITY_MIRROR_LABEL,
        )
        self.assertIn("MIRROR", identity["identity_authority"])
        self.assertIn("HTTP 403", identity["identity_diagnostics"])

    def test_mirror_is_identity_only(self):
        mirror = f._parse_sec_identity_mirror({"1018724": "AMZN"})
        self.assertEqual(mirror["AMZN"]["cik"], 1018724)
        self.assertNotIn("revenue", mirror["AMZN"])
        self.assertNotIn("earnings", mirror["AMZN"])

    def test_companyfacts_cik_must_match_requested_identity(self):
        payload = {
            "cik": 9999999,
            "entityName": "Wrong issuer",
            "facts": {"us-gaap": {"Revenues": {}}},
        }
        with patch(
            "requests.Session.get",
            return_value=resp(200, json_payload=payload),
        ):
            with self.assertRaises(f.SecAccessError) as ctx:
                f.fetch_sec_companyfacts(
                    1018724,
                    user_agent="TradeWithEdge Test test@example.com",
                )

        self.assertEqual(
            ctx.exception.stage,
            "SEC COMPANYFACTS IDENTITY VALIDATION",
        )

    def test_companyfacts_correct_cik_passes_transport_validation(self):
        payload = {
            "cik": 1018724,
            "entityName": "AMAZON COM INC",
            "facts": {"us-gaap": {"Revenues": {}}},
        }
        with patch(
            "requests.Session.get",
            return_value=resp(200, json_payload=payload),
        ):
            result = f.fetch_sec_companyfacts(
                1018724,
                user_agent="TradeWithEdge Test test@example.com",
            )

        self.assertEqual(result["cik"], 1018724)


if __name__ == "__main__":
    unittest.main()
