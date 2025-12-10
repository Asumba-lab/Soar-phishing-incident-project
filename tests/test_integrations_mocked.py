import os
import unittest
from unittest.mock import patch, Mock

import importlib


class MockedExternalAPITests(unittest.TestCase):
    def setUp(self):
        # Ensure env keys are present to exercise integration branches
        os.environ["VIRUSTOTAL_API_KEY"] = "fake"
        os.environ["ABUSEIPDB_API_KEY"] = "fake"
        os.environ["OKTA_API_TOKEN"] = "fake"
        os.environ["OKTA_DOMAIN"] = "example.okta.com"
        os.environ["MS_GRAPH_TOKEN"] = "fake"

    def tearDown(self):
        for k in ("VIRUSTOTAL_API_KEY", "ABUSEIPDB_API_KEY", "OKTA_API_TOKEN", "OKTA_DOMAIN", "MS_GRAPH_TOKEN"):
            os.environ.pop(k, None)

    @patch("enrich_iocs.requests.get")
    @patch("enrich_iocs.requests.post")
    def test_enrichment_uses_external_apis(self, mock_post, mock_get):
        # Mock VirusTotal URL lookup via POST
        vt_post_resp = Mock()
        vt_post_resp.raise_for_status = Mock()
        vt_post_resp.json.return_value = {"data": {"id": "vt-url-1"}}
        mock_post.return_value = vt_post_resp

        # Mock AbuseIPDB/VT hash lookups via GET
        get_resp = Mock()
        get_resp.raise_for_status = Mock()
        # abuseipdb GET returns data in a 'data' key
        get_resp.json.side_effect = [
            {"data": {"abuseConfidenceScore": 42}},
            {"data": {"attributes": {"last_analysis_stats": {"malicious": 3}}}},
        ]
        mock_get.return_value = get_resp

        # Import module after env vars set so it picks up the API keys
        enrich_mod = importlib.reload(importlib.import_module("enrich_iocs"))
        sample = {"emails": ["a@b.com"], "urls": ["http://example.com/bad"], "ips": ["1.2.3.4"], "hashes": ["a" * 32]}
        out = enrich_mod.enrich_iocs(sample)

        # Ensure external API calls were attempted
        self.assertTrue(mock_post.called, "VirusTotal POST was not called")
        self.assertTrue(mock_get.called, "GET (AbuseIPDB/VT) was not called")

        # Ensure results include expected keys
        self.assertIn("http://example.com/bad", out["urls"])
        self.assertIn("1.2.3.4", out["ips"])

    @patch("isolate_account.requests.get")
    @patch("isolate_account.requests.post")
    def test_isolate_account_okta_flow(self, mock_post, mock_get):
        # Simulate Okta user lookup and suspend
        user_resp = Mock()
        user_resp.status_code = 200
        user_resp.json.return_value = {"id": "user-123"}
        mock_get.return_value = user_resp

        suspend_resp = Mock()
        suspend_resp.status_code = 200
        mock_post.return_value = suspend_resp

        # Import isolate_account after env vars set so module-level tokens are loaded
        iso_mod = importlib.reload(importlib.import_module("isolate_account"))
        res = iso_mod.isolate_account("user@example.com")
        self.assertEqual(res.get("action"), "suspended_okta")


if __name__ == "__main__":
    unittest.main()
