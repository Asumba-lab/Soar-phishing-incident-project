"""Demo runner that simulates a SOAR phishing incident response playbook.

This script ties together IOC extraction, enrichment, risk scoring and containment.
"""

import json
from extract_iocs import extract_iocs
from enrich_iocs import enrich_iocs
from risk_score import compute_risk_score
from containment import perform_containment


SAMPLE_EMAIL = """
From: attacker@example.com
To: victim_user@example.com
Subject: Invoice Attached

Hi,
Please review the attached invoice at https://malicious.example.com/invoice.pdf
Contact: attacker@example.com
File hash: d41d8cd98f00b204e9800998ecf8427e
"""


def run_demo(email_text: str = None) -> dict:
    text = email_text or SAMPLE_EMAIL
    print("[+] Extracting IOCs...")
    iocs = extract_iocs(text)
    print(json.dumps(iocs, indent=2))

    print("[+] Enriching IOCs...")
    enriched = enrich_iocs(iocs)
    print(json.dumps(enriched, indent=2))

    print("[+] Computing risk score...")
    score = compute_risk_score(iocs, enriched)
    print(f"Risk score: {score}")

    result = {"iocs": iocs, "enriched": enriched, "risk_score": score}

    if score >= 80:
        print("[!] High risk detected — taking containment action...")
        actions = perform_containment("victim_user@example.com", iocs)
        result["containment"] = actions
        print(json.dumps(actions, indent=2))
    else:
        print("[-] Risk below containment threshold.")

    # write outputs for artifacts/screenshots
    with open("playbook_output.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    return result


if __name__ == "__main__":
    out = run_demo()
    print("[+] Demo complete — output saved to playbook_output.json")
