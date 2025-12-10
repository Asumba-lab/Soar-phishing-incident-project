"""Simple risk scoring for the demo playbook."""

from typing import Dict


def compute_risk_score(iocs: Dict[str, list], enriched: Dict[str, dict]) -> int:
    """Compute a basic risk score (0-100).

    Heuristic: base points per IOC + extra for suspicious enrichment.
    """
    score = 0
    # base points
    score += len(iocs.get("emails", [])) * 10
    score += len(iocs.get("urls", [])) * 15
    score += len(iocs.get("ips", [])) * 10
    score += len(iocs.get("hashes", [])) * 20

    # enrichment adjustments
    for e, meta in (enriched.get("emails", {}) or {}).items():
        if meta.get("reputation") == "suspicious":
            score += 10
    for u, meta in (enriched.get("urls", {}) or {}).items():
        if meta.get("reputation") == "malicious":
            score += 20

    return min(score, 100)


if __name__ == "__main__":
    sample_iocs = {
        "emails": ["attacker@example.com"],
        "urls": ["https://malicious.example.com/login"],
        "ips": [],
        "hashes": [],
    }
    from enrich_iocs import enrich_iocs

    enriched = enrich_iocs(sample_iocs)
    print("Risk score:", compute_risk_score(sample_iocs, enriched))
