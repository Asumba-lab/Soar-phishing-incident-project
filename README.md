# SOAR Phishing Incident Response — Demo Playbook

This repository demonstrates a simple, auditable SOAR-style phishing incident response playbook implemented in Python. It is intended for learning, prototyping, and capstone/demo use. Integrations with third-party services and identity providers are optional and are safe by default: if API keys are not provided, the code uses simulated, non-destructive fallbacks.

**Core goals**
- Show an end-to-end flow: IOC extraction → enrichment → risk scoring → approval (optional) → containment.
- Provide clear, auditable actions and an approval webhook for human-in-the-loop decisioning.
- Ship a testable demo with mocked integrations and CI-friendly tests.

**Important**: Do not store secrets or production API keys in this repository. Use environment variables or a secrets manager. See `docs/secrets.md` and `.env.template` for recommended patterns.

#### Table of contents
- Project overview
- Quickstart (local)
- Running with webhook approval
- Environment variables and secrets
- Audit, logging and approval details
- Testing and CI
- Docker
- How to extend
- Security considerations
- Troubleshooting
- Contributing

---

#### Project overview
- `extract_iocs.py` — Extracts emails, URLs, IPs, and hashes from message text.
- `enrich_iocs.py` — Optional enrichment using VirusTotal, AbuseIPDB, and local stubs.
- `risk_score.py` — Heuristic scoring to produce a 0–100 risk value.
- `containment.py` — High-level orchestration: isolate account, reset password, enforce MFA, block domains, quarantine emails.
- `isolate_account.py` — Identity provider helpers (Okta / MS Graph) used by `containment.py`.
- `approval.py` — Supervisor approval helper supporting `cli`, `email` (simulated), and `webhook` modes.
- `approval_server.py` — Lightweight Flask server for testing webhook-based approvals.
- `audit.py` — Centralized audit logging with rotation, optional HMAC signing, and optional forwarding to an external audit collector.
- `playbook_demo.py` — Demo runner that ties everything together and writes `playbook_output.json`.

---

#### Quickstart (local, Windows PowerShell)
1. Create and activate a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Run the demo (safe defaults — no destructive actions):

```powershell
python .\playbook_demo.py
```

3. Inspect artifacts:
- `playbook_output.json` — JSON transcript with `iocs`, `enriched`, `risk_score`, and `containment` (if executed).
- `logs/playbook.log` — newline-delimited JSON audit entries (created when approval is required or containment executes).

---

#### Running with webhook approval (human-in-the-loop)
This project supports a webhook approval mode where the playbook posts an approval request and waits for an explicit allow/deny.

1. Start the approval server (demo helper) in a separate shell:

```powershell
python approval_server.py
```

2. Run the demo with webhook approval enabled (demo picks up env vars at runtime):

```powershell
$env:REQUIRE_APPROVAL='true'; $env:APPROVAL_MODE='webhook'; $env:APPROVAL_WEBHOOK_URL='http://localhost:5000/request'; $env:APPROVAL_STATUS_URL='http://localhost:5000/status/{id}'; python .\playbook_demo.py
```

3. When the `approval_server` prints a request id, approve it by calling the callback endpoint (replace <id> accordingly):

```powershell
curl -X POST -H "Content-Type: application/json" -d '{"approved": true, "approver": "alice"}' http://localhost:5000/callback/<id>
```

The demo will poll the status endpoint and proceed or abort containment depending on the response.

---

#### Environment variables & secrets
Use environment variables (or a CI secrets store) to enable real integrations. The `.env.template` file lists supported variables.

- `VIRUSTOTAL_API_KEY` — VirusTotal v3 API key (optional).
- `ABUSEIPDB_API_KEY` — AbuseIPDB key (optional).
- `MS_DEFENDER_KEY` — Microsoft Defender demo key (optional).
- `OKTA_API_TOKEN`, `OKTA_DOMAIN` — Okta admin token and base domain (only enable if you understand the effects).
- `MS_GRAPH_TOKEN` — Microsoft Graph token with appropriate permissions (only enable if you understand the effects).
- `REQUIRE_APPROVAL` — set to `true` to require approval before containment.
- `APPROVAL_MODE` — `cli`, `email`, or `webhook`.
- `APPROVAL_WEBHOOK_URL`, `APPROVAL_STATUS_URL` — webhook endpoints when `APPROVAL_MODE=webhook`.
- `AUDIT_HMAC_SECRET` — optional secret to sign audit entries (HMAC-SHA256).
- `AUDIT_SERVICE_URL` — optional external audit collector URL to POST entries to.

Never commit secrets to source control. For CI, store them in GitHub Actions Secrets or your CI provider's secrets storage.

---

#### Audit & logging
- `audit.py` writes newline-delimited JSON audit records to `logs/playbook.log` by default and uses rotation (default 5MB, 3 backups). Configure via env vars: `AUDIT_LOG_PATH`, `AUDIT_LOG_MAX_BYTES`, `AUDIT_LOG_BACKUP_COUNT`.
- When `AUDIT_HMAC_SECRET` is set, entries are HMAC-signed and the signature is attached as `_hmac` in the log record; when `AUDIT_SERVICE_URL` is set, entries are POSTed to that endpoint as an external backup.
- Audit entries include timestamp, account, proposed actions, approval decision, and results.

Recommendations:
- Forward audit logs to a secure, centralized collector (SIEM, S3 with restricted access, or a write-once store). Do not rely only on local container storage in production.
- Enable `AUDIT_HMAC_SECRET` to detect tampering between local and remote copies.

---

#### Testing & CI
- Tests live in `tests/`. Some tests use mocks to exercise integration codepaths safely.
- New tests include `tests/test_approval_audit.py` which mocks webhook approval flow and asserts audit logging behavior.
- CI (`.github/workflows/ci.yml`) runs:
	- `black --check .` (formatting)
	- `flake8` (linting)
	- `python -m unittest discover -v` (tests)

For deterministic integration testing, consider adding `vcrpy` recordings for external TI vendors so CI can replay responses without live keys.

---

#### Docker
- The `Dockerfile` builds a minimal image, installs dependencies, runs as a non-root user, and includes `tini` for signal handling.
- Build and run (PowerShell):

```powershell
docker build -t soar-phish-demo:latest .
docker run --rm soar-phish-demo:latest
```

Notes: If you plan to use Docker containers in production, ensure the container has secure access to your audit collector and that secrets are injected securely (e.g., via a secrets manager or runtime injection in your orchestration platform).

---

#### How to extend
- Add more threat-intel providers and caching for enrichment.
- Add vcrpy fixtures or recorded HTTP fixtures for deterministic CI integration tests.
- Implement a production-ready approval service with authentication, an approval UI, audit trail, and durable storage (e.g., PostgreSQL).
- Integrate with a ticketing system (ServiceNow, Jira) to create incidents automatically.

---

#### Security considerations & best practices
- Always test with simulated/safe endpoints before running destructive operations.
- Limit privileges of tokens used for containment (use scoped admin accounts and break-glass procedures).
- Use RBAC and multi-person approval for high-impact actions.
- Protect `AUDIT_HMAC_SECRET` and `AUDIT_SERVICE_URL` and rotate them periodically.

---

#### Troubleshooting
- If tests do not run, ensure your virtual environment is active and dependencies are installed.
- If the approval webhook times out, confirm the `approval_server.py` is reachable and that `APPROVAL_WEBHOOK_URL` and `APPROVAL_STATUS_URL` are configured correctly.

---

#### Contributing
- Open issues for features or bugs. For production-readiness changes (real integrations, persistent approval stores), include tests and an audit plan.

---

Artifacts
- Operator runbook: `docs/runbook.md` (triage, approval, rollback, audit review).
- 5-slide summary deck: `presentation/5_slide_deck.md` (architecture and runbook highlights).
