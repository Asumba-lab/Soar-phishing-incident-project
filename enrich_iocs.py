"""IOC enrichment utilities.

This module provides a simple enrichment implementation and optional
integration with external threat-intel services when API keys are set in
environment variables. Supported (optional) integrations:
- VirusTotal v3 for hash/url lookup via `VIRUSTOTAL_API_KEY`.
- AbuseIPDB for IP reputation via `ABUSEIPDB_API_KEY`.

If API keys are not present the function falls back to simulated data so
the demo remains runnable offline.
"""

from typing import Dict, Any
import os
import requests


VT_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_API_KEY")


def _vt_lookup_hash(hsh: str) -> Dict[str, Any]:
    """Lookup a file hash in VirusTotal v3. Returns a minimal result dict.

    Requires `VIRUSTOTAL_API_KEY` in env. If missing, returns an empty dict.
    """
    if not VT_API_KEY:
        return {}
    url = f"https://www.virustotal.com/api/v3/files/{hsh}"
    headers = {"x-apikey": VT_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        # extract a couple of useful fields if present
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats")
        return {"vt_last_analysis": stats}
    except Exception:
        return {"vt_error": True}


def _vt_lookup_url(url_str: str) -> Dict[str, Any]:
    if not VT_API_KEY:
        return {}
    url = "https://www.virustotal.com/api/v3/urls"
    headers = {"x-apikey": VT_API_KEY}
    try:
        r = requests.post(url, headers=headers, data={"url": url_str}, timeout=10)
        r.raise_for_status()
        lookup = r.json()
        return {"vt_lookup": lookup}
    except Exception:
        return {"vt_error": True}


def _abuseipdb_lookup(ip: str) -> Dict[str, Any]:
    if not ABUSEIPDB_KEY:
        return {}
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return {"abuseipdb": r.json().get("data")}
    except Exception:
        return {"abuse_error": True}


def _ms_defender_lookup(value: str) -> Dict[str, Any]:
    """Simulated Microsoft Defender TI lookup.

    If `MS_DEFENDER_KEY` is set in the environment this function would
    contact the real API; in this demo it returns a simulated response
    to allow demonstration of integration points.
    """
    # For demo purposes we only simulate. Real integration would use
    # the Microsoft Defender ATP APIs and auth flow.
    if not os.environ.get("MS_DEFENDER_KEY"):
        return {}
    # Simulated response
    return {"ms_defender": {"threats_found": 0, "confidence": "low"}}


def enrich_iocs(iocs: Dict[str, list]) -> Dict[str, Any]:
    """Return enrichment map for provided IOCs.

    If external API keys are available, call those services; otherwise
    return simulated enrichment that is useful for demos and testing.
    """
    enriched = {"emails": {}, "urls": {}, "ips": {}, "hashes": {}}

    for e in iocs.get("emails", []):
        enriched["emails"][e] = {
            "reputation": "suspicious",
            "owner": e.split("@")[-1],
        }

    for u in iocs.get("urls", []):
        entry = {"reputation": "malicious" if "malicious" in u else "unknown"}
        vt = _vt_lookup_url(u)
        if vt:
            entry.update(vt)
        enriched["urls"][u] = entry

    for ip in iocs.get("ips", []):
        entry = {"geo": "Unknown", "reputation": "suspicious"}
        abuse = _abuseipdb_lookup(ip)
        if abuse:
            entry.update(abuse)
        enriched["ips"][ip] = entry

    for h in iocs.get("hashes", []):
        entry = {"malware_family": None, "known_bad": False}
        vt = _vt_lookup_hash(h)
        if vt:
            entry.update(vt)
        enriched["hashes"][h] = entry

    return enriched


if __name__ == "__main__":
    import json

    sample = {
        "emails": ["attacker@example.com"],
        "urls": ["https://malicious.example.com/login"],
        "ips": ["192.0.2.1"],
        "hashes": ["d41d8cd98f00b204e9800998ecf8427e"],
    }
    print(json.dumps(enrich_iocs(sample), indent=2))
