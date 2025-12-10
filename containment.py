"""Containment orchestration helpers for the demo.

Provides a high-level `perform_containment` that calls identity and
email gateway actions. Actions are simulated unless the corresponding
API environment variables are configured.
"""
from typing import Dict, List

from isolate_account import isolate_account


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
    results = {}
    results["isolate"] = isolate_account(account_identifier)
    results["reset_password"] = reset_password(account_identifier)
    results["enforce_mfa"] = enforce_mfa(account_identifier)

    # block domains found in IOCs
    domains = set()
    for u in iocs.get("urls", []):
        try:
            parts = u.split("//", 1)[1]
            domain = parts.split("/", 1)[0]
            domains.add(domain)
        except Exception:
            continue
    results["blocked_domains"] = {d: block_domain(d) for d in sorted(domains)}

    # quarantine any emails found
    results["quarantine"] = quarantine_emails(iocs.get("emails", []))

    return results


if __name__ == "__main__":
    print(perform_containment("victim_user@example.com", {"urls": ["https://malicious.example.com/invoice.pdf"], "emails": ["victim_user@example.com"]}))
