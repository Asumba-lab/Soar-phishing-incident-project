"""Containment helpers.

This module will attempt to perform real containment using Okta or
Microsoft Graph APIs when appropriate environment variables are set.

Environment variables supported:
- `OKTA_API_TOKEN` and `OKTA_DOMAIN` to call Okta user lifecycle APIs.
- `MS_GRAPH_TOKEN` to call Microsoft Graph to disable a user.

If no credentials are present, actions are simulated for demo/testing.
"""

import os
from typing import Dict
import requests


OKTA_TOKEN = os.environ.get("OKTA_API_TOKEN")
OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN")
MS_GRAPH_TOKEN = os.environ.get("MS_GRAPH_TOKEN")


def isolate_account(account_identifier: str) -> Dict[str, object]:
    """Attempt to isolate an account. Returns an action result dict.

    The `account_identifier` should be an email or user id. This function
    first tries Okta (if configured), then Microsoft Graph. If neither is
    configured, a simulated response is returned.
    """
    # Try Okta if configured
    if OKTA_TOKEN and OKTA_DOMAIN:
        try:
            # Okta: Suspend user lifecycle (requires the Okta userId)
            headers = {
                "Authorization": f"SSWS {OKTA_TOKEN}",
                "Accept": "application/json",
            }
            # In a real integration you would resolve the user id from email.
            # Here we naively attempt to search by login (email) using the API.
            search_url = f"https://{OKTA_DOMAIN}/api/v1/users/{account_identifier}"
            r = requests.get(search_url, headers=headers, timeout=10)
            if r.status_code == 200:
                user = r.json()
                user_id = user.get("id")
                suspend_url = (
                    f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/suspend"
                )
                rs = requests.post(suspend_url, headers=headers, timeout=10)
                if rs.status_code in (200, 204):
                    return {
                        "account": account_identifier,
                        "action": "suspended_okta",
                        "okta_status": rs.status_code,
                    }
                return {
                    "account": account_identifier,
                    "action": "okta_failed",
                    "status": rs.status_code,
                }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "account": account_identifier,
                "action": "okta_error",
                "error": str(exc),
            }

    # Try Microsoft Graph if configured
    if MS_GRAPH_TOKEN:
        try:
            headers = {
                "Authorization": f"Bearer {MS_GRAPH_TOKEN}",
                "Content-Type": "application/json",
            }
            # Attempt to find user by userPrincipalName (email)
            search_url = f"https://graph.microsoft.com/v1.0/users/{account_identifier}"
            r = requests.get(search_url, headers=headers, timeout=10)
            if r.status_code == 200:
                user = r.json()
                user_id = user.get("id")
                patch_url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
                body = {"accountEnabled": False}
                rs = requests.patch(patch_url, headers=headers, json=body, timeout=10)
                if rs.status_code in (200, 204):
                    return {
                        "account": account_identifier,
                        "action": "disabled_graph",
                        "graph_status": rs.status_code,
                    }
                return {
                    "account": account_identifier,
                    "action": "graph_failed",
                    "status": rs.status_code,
                }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "account": account_identifier,
                "action": "graph_error",
                "error": str(exc),
            }

    # Fallback: simulated isolation (demo)
    return {
        "account": account_identifier,
        "action": "isolated",
        "details": "simulated - no API keys configured",
    }


if __name__ == "__main__":
    print(isolate_account("victim_user@example.com"))
