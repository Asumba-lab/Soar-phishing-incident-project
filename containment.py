"""Containment orchestration helpers for the demo.

Provides a high-level `perform_containment` that calls identity and
email gateway actions. Actions are simulated unless the corresponding
API environment variables are configured.
"""
from typing import Dict, List
import os
import json
from datetime import datetime
import logging
from audit import log_audit

from isolate_account import isolate_account
from approval import get_approval

logger = logging.getLogger(__name__)




def reset_password(account_identifier: str) -> Dict[str, object]:
    # Delegate to identity provider if implemented in `isolate_account`,
    # otherwise return a simulated response.
    try:
        # Try to call an optional helper in isolate_account if present
        from isolate_account import reset_password as _rp  # type: ignore

        return _rp(account_identifier)
    except Exception:
        return {"account": account_identifier, "action": "password_reset_simulated"}


def enforce_mfa(account_identifier: str) -> Dict[str, object]:
    try:
        from isolate_account import enforce_mfa as _em  # type: ignore

        return _em(account_identifier)
    except Exception:
        return {"account": account_identifier, "action": "enforce_mfa_simulated"}


def block_domain(domain: str) -> Dict[str, object]:
    try:
        from isolate_account import block_domain as _bd  # type: ignore

        return _bd(domain)
    except Exception:
        return {"domain": domain, "action": "blocked_simulated"}


def quarantine_emails(iocs: List[str]) -> Dict[str, object]:
    try:
        from isolate_account import quarantine_emails as _qe  # type: ignore

        return _qe(iocs)
    except Exception:
        return {"quarantined": iocs, "action": "quarantine_simulated"}


def perform_containment(account_identifier: str, iocs: Dict[str, list]) -> Dict[str, object]:
    # Build the proposed action summary for approval/audit
    domains = set()
    for u in iocs.get("urls", []):
        try:
            parts = u.split("//", 1)[1]
            domain = parts.split("/", 1)[0]
            domains.add(domain)
        except Exception:
            continue

    proposed_actions = {
        "isolate": True,
        "reset_password": True,
        "enforce_mfa": True,
        "blocked_domains": sorted(domains),
        "quarantine_emails": iocs.get("emails", []),
    }

    approved = get_approval(account_identifier, proposed_actions)

    audit_entry = {
        "account": account_identifier,
        "proposed_actions": proposed_actions,
        "approved": bool(approved),
    }

    if not approved:
        audit_entry["outcome"] = "denied"
        try:
            log_audit(audit_entry)
        except Exception:
            logger.exception("Failed to write audit log for denied approval")

        return {"approved": False, "reason": "supervisor_denied"}

    # Execute containment actions
    results = {}
    results["isolate"] = isolate_account(account_identifier)
    results["reset_password"] = reset_password(account_identifier)
    results["enforce_mfa"] = enforce_mfa(account_identifier)

    results["blocked_domains"] = {d: block_domain(d) for d in sorted(domains)}

    results["quarantine"] = quarantine_emails(iocs.get("emails", []))

    audit_entry["outcome"] = "executed"
    audit_entry["results"] = results

    try:
        log_audit(audit_entry)
    except Exception:
        logger.exception("Failed to write audit log after containment execution")

    return {"approved": True, "results": results}


if __name__ == "__main__":
    print(perform_containment("victim_user@example.com", {"urls": ["https://malicious.example.com/invoice.pdf"], "emails": ["victim_user@example.com"]}))
