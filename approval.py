"""Supervisor approval helpers.

Provides a simple approval stub that can operate in CLI mode or email-stub mode.
"""
import os
import logging
import time
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


def get_approval(account_identifier: str, actions: dict) -> bool:
    """Return True if supervisor approves containment.

    Behavior is controlled by environment variables:
    - REQUIRE_APPROVAL: if 'true', approval is required; otherwise approval is implicit.
    - APPROVAL_MODE: 'cli' to prompt on the command line, 'email' to simulate sending an email.
    """
    require = os.environ.get("REQUIRE_APPROVAL", "false").lower() == "true"
    if not require:
        logger.debug("Approval not required by configuration")
        return True

    mode = os.environ.get("APPROVAL_MODE", "cli").lower()
    if mode == "cli":
        try:
            print("Supervisor approval required for containment on account:", account_identifier)
            print("Proposed actions:")
            for k, v in actions.items():
                print(f" - {k}: {v}")
            resp = input("Approve containment? (yes/no): ").strip().lower()
            approved = resp in ("y", "yes")
            logger.info("CLI approval result: %s", approved)
            return approved
        except Exception:
            logger.exception("Error while collecting CLI approval")
            return False

    # Simulate email approval (for demo only)
    if mode == "email":
        logger.info("Simulating sending approval email for account %s", account_identifier)
        # In a real implementation send an email/webhook and wait for callback
        return False

    # Webhook mode: POST the approval request to a webhook endpoint and poll for status
    if mode == "webhook":
        webhook = os.environ.get("APPROVAL_WEBHOOK_URL", "http://localhost:5000/request")
        wait_seconds = int(os.environ.get("APPROVAL_WAIT_SECONDS", "60"))
        poll_interval = float(os.environ.get("APPROVAL_POLL_INTERVAL", "2"))

        payload: Dict[str, Any] = {"account": account_identifier, "proposed_actions": actions}
        try:
            resp = requests.post(webhook, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            req_id = data.get("id")
            if not req_id:
                logger.warning("Webhook returned no request id; denying")
                return False
        except Exception:
            logger.exception("Failed to post approval request to %s", webhook)
            return False

        status_url = os.environ.get("APPROVAL_STATUS_URL", webhook.rstrip("/request") + "/status/{id}")
        # Poll for result until timeout
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            try:
                st = status_url.format(id=req_id)
                r = requests.get(st, timeout=5)
                r.raise_for_status()
                js = r.json()
                if js.get("status") == "approved":
                    logger.info("Webhook approval received for %s", account_identifier)
                    return True
                if js.get("status") == "denied":
                    logger.info("Webhook denial received for %s", account_identifier)
                    return False
            except Exception:
                logger.debug("Waiting for approval callback...", exc_info=False)
            time.sleep(poll_interval)

        logger.warning("Approval webhook timed out for %s", account_identifier)
        return False

    logger.warning("Unknown approval mode '%s' — denying by default", mode)
    return False
