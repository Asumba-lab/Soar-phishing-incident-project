import os
import unittest
from unittest.mock import patch, Mock
import importlib


class ApprovalAuditTests(unittest.TestCase):
    def setUp(self):
        os.environ["REQUIRE_APPROVAL"] = "true"
        os.environ["APPROVAL_MODE"] = "webhook"
        os.environ["APPROVAL_WEBHOOK_URL"] = "http://localhost/request"
        os.environ["APPROVAL_STATUS_URL"] = "http://localhost/status/{id}"
        os.environ["APPROVAL_WAIT_SECONDS"] = "5"
        os.environ["APPROVAL_POLL_INTERVAL"] = "0.01"

    def tearDown(self):
        for k in (
            "REQUIRE_APPROVAL",
            "APPROVAL_MODE",
            "APPROVAL_WEBHOOK_URL",
            "APPROVAL_STATUS_URL",
            "APPROVAL_WAIT_SECONDS",
            "APPROVAL_POLL_INTERVAL",
        ):
            os.environ.pop(k, None)

    @patch("audit.log_audit")
    @patch("requests.get")
    @patch("requests.post")
    @patch("containment.isolate_account")
    def test_webhook_approval_executes_and_logs(self, mock_isolate, mock_post, mock_get, mock_log):
        # isolate_account should be harmlessly stubbed
        mock_isolate.return_value = {"action": "suspended_simulated"}

        # POST returns an id
        post_resp = Mock()
        post_resp.raise_for_status = Mock()
        post_resp.json.return_value = {"id": "req-1"}
        mock_post.return_value = post_resp

        # GET returns pending then approved
        get_resp_pending = Mock()
        get_resp_pending.raise_for_status = Mock()
        get_resp_pending.json.return_value = {"status": "pending"}

        get_resp_approved = Mock()
        get_resp_approved.raise_for_status = Mock()
        get_resp_approved.json.return_value = {"status": "approved"}

        mock_get.side_effect = [get_resp_pending, get_resp_approved]

        # Reload modules to pick up env
        importlib.reload(importlib.import_module("approval"))
        importlib.reload(importlib.import_module("containment"))

        cont_mod = importlib.import_module("containment")
        res = cont_mod.perform_containment("victim@example.com", {"urls": [], "emails": []})

        self.assertTrue(res.get("approved"))
        # Ensure audit.log_audit called and 'executed' present
        self.assertTrue(mock_log.called)
        called_with = mock_log.call_args[0][0]
        self.assertEqual(called_with.get("outcome"), "executed")

    @patch("audit.log_audit")
    @patch("requests.get")
    @patch("requests.post")
    @patch("containment.isolate_account")
    def test_webhook_denial_is_logged(self, mock_isolate, mock_post, mock_get, mock_log):
        mock_isolate.return_value = {"action": "suspended_simulated"}

        post_resp = Mock()
        post_resp.raise_for_status = Mock()
        post_resp.json.return_value = {"id": "req-2"}
        mock_post.return_value = post_resp

        get_resp_denied = Mock()
        get_resp_denied.raise_for_status = Mock()
        get_resp_denied.json.return_value = {"status": "denied"}
        mock_get.return_value = get_resp_denied

        importlib.reload(importlib.import_module("approval"))
        importlib.reload(importlib.import_module("containment"))

        cont_mod = importlib.import_module("containment")
        res = cont_mod.perform_containment("victim@example.com", {"urls": [], "emails": []})

        self.assertFalse(res.get("approved"))
        self.assertTrue(mock_log.called)
        called_with = mock_log.call_args[0][0]
        self.assertEqual(called_with.get("outcome"), "denied")


if __name__ == "__main__":
    unittest.main()
