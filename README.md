# SOAR Phishing Incident Response (Demo)
**SOAR Phishing Incident Response System**

- **Purpose:** Demonstrate a complete SOAR playbook for phishing: IOC extraction, TI enrichment, risk scoring and automated containment.
- **Scope:** Educational/demo-capstone level. Integrations are optional and safe by default (simulated fallbacks used when API keys are not provided).

**Project Overview**
- The repository contains a runnable Python demo that shows an end-to-end phishing playbook: it ingests a sample phishing email, extracts IOCs, enriches them (optionally using third-party TI), computes a risk score, and triggers containment when the score meets the threshold.

**Quick Start**
- Prerequisites: Python 3.10+ and Git (optional).
- Create and activate a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

- Run the demo:

```powershell
python .\playbook_demo.py
```

**Key Outputs**
- `playbook_output.json`: full JSON artifact with `iocs`, `enriched`, `risk_score`, and `containment` (if executed).
- `tests/`: unit and mocked integration tests.

**Environment / Integration Keys**
Set these as environment variables when you want the demo to call real services. If not present, the demo will run using safe simulated responses.

- VirusTotal: `VIRUSTOTAL_API_KEY`
- AbuseIPDB: `ABUSEIPDB_API_KEY`
- Microsoft Defender (demo stub): `MS_DEFENDER_KEY`
- Okta: `OKTA_API_TOKEN` and `OKTA_DOMAIN` (e.g. `dev-123456.okta.com`)
- Microsoft Graph: `MS_GRAPH_TOKEN`

Example (PowerShell):
```powershell
setx VIRUSTOTAL_API_KEY "<your_key>"
setx ABUSEIPDB_API_KEY "<your_key>"
setx OKTA_API_TOKEN "<your_okta_token>"
setx OKTA_DOMAIN "dev-123456.okta.com"
setx MS_GRAPH_TOKEN "<ms_graph_oauth_token>"
```

**Playbook Behavior & Thresholds**
- IOC extraction: `extract_iocs.py` extracts emails, URLs, IPs, and hashes using regex.
- Enrichment: `enrich_iocs.py` performs optional VirusTotal/AbuseIPDB lookups and a Microsoft Defender stub; results augment IOCs for scoring.
- Risk Scoring: `risk_score.py` computes a 0-100 score using IOC counts and enrichment indicators.
- Containment: `containment.py` orchestrates containment steps (disable account, reset password, enforce MFA, block domains, quarantine emails) and is executed when `risk_score >= 80`.

**Files of Interest**
- `extract_iocs.py` — IOC extraction helpers
- `enrich_iocs.py` — enrichment with optional TI integrations
- `risk_score.py` — scoring logic (adjust heuristics here)
- `isolate_account.py` — identity provider helpers (Okta / MS Graph)
- `containment.py` — containment orchestration that calls identity and email actions
- `playbook_demo.py` — main orchestrator and demo runner
- `phishing_soar_playbook.json` — JSON representation of the playbook and its steps

**Testing & CI**
- Unit tests: `tests/test_playbook.py`
- Mocked integration tests: `tests/test_integrations_mocked.py` (mocks external APIs so CI can run without secrets).
- CI workflow: `.github/workflows/ci.yml` runs formatting (`black`), linting (`flake8`) and tests. Add secrets in GitHub Actions to exercise real integrations.

**Docker**
- A minimal `Dockerfile` is included to run the demo in a container. To build and run:

```powershell
docker build -t soar-phish-demo:latest .
docker run --rm soar-phish-demo:latest
```

**Security & Safety Notes**
- The repository defaults to simulated, non-destructive behavior. Do not add real API keys to public repositories.
- When enabling real containment actions (Okta/MS Graph), ensure you have the correct administrative permissions, auditing, and change control in place.

**Extending This Project**
- Add more TI vendors and caching for enrichment.
- Add integration tests that use recorded HTTP fixtures (e.g., `vcrpy`) for deterministic CI runs.
- Replace simulated containment steps with audited, idempotent APIs and add RBAC checks.

**Contribution & Support**
- Open an issue or PR with suggested improvements. For production integrations, include tests and a clear rollback strategy.

**License & Attribution**
- This demo is provided for educational purposes. Add a license file if you intend to redistribute.
