# Operator Runbook — SOAR Phishing Incident Response Demo

This runbook describes operator steps to triage, approve, execute, and audit a phishing containment playbook run using the demo code in this repository. It is written for on-call operators and incident responders using the repository in a test or demo environment. For production usage, adapt policies, authentication, and deployment details accordingly.

## Before you begin

- Confirm access: ensure you have access to the environment where the playbook runs (local machine, container host, or orchestrator).
- Ensure secrets: verify any required secrets are available via environment variables or a secrets manager (do not store secrets in source control). See `.env.template` and `docs/secrets.md`.
- Verify audit collector: check `AUDIT_SERVICE_URL` (if configured) is reachable and that `AUDIT_HMAC_SECRET` is set if signatures are expected.

## Quick commands

- Run the demo locally (safe defaults):
```
python playbook_demo.py
```

- Run the demo with webhook approval enabled (example):
```
$env:REQUIRE_APPROVAL='true'; $env:APPROVAL_MODE='webhook'; $env:APPROVAL_WEBHOOK_URL='http://localhost:5000/request'; $env:APPROVAL_STATUS_URL='http://localhost:5000/status/{id}'; python playbook_demo.py
```

- Start the demo approval server (for manual approval flows):
```
python approval_server.py
```

## Triage checklist (when alerted)

1. Gather context:
   - Source system and sample message (email headers, body).
   - Affected account(s) and business criticality.
2. Run IOC extraction locally to view suspected indicators:
   - `python -c "from extract_iocs import extract_iocs; print(extract_iocs(open('sample.eml').read()))"`
3. Enrich indicators (optionally with real TI keys):
   - Ensure `VIRUSTOTAL_API_KEY` / `ABUSEIPDB_API_KEY` are set if using external enrichments.
4. Compute risk:
   - The demo sets a containment threshold at 80. Review `risk_score.py` for scoring heuristics.

## Approval workflow (human-in-the-loop)

Modes supported:
- `cli` — prompts the operator on the running console.
- `webhook` — posts an approval request to an HTTP endpoint and polls a status URL.
- `email` — simulated notification (demo only).

Operator steps for webhook mode:
1. Start `approval_server.py` (or ensure a production approval endpoint is available).
2. Trigger the playbook run with `REQUIRE_APPROVAL=true` and `APPROVAL_MODE=webhook` set.
3. The playbook will POST a request to `APPROVAL_WEBHOOK_URL` and print a request id in the approval server logs.
4. Approve or deny via the approval server callback (or UI):
   - Approve: POST `{"approved": true, "approver": "alice"}` to `/callback/<id>`
   - Deny: POST `{"approved": false, "approver": "alice"}` to `/callback/<id>`
5. The playbook polls `APPROVAL_STATUS_URL` and proceeds if approved.

## Containment steps (executed by the playbook)

When approval is granted (or approval not required), the playbook will perform the following, in order:
1. `isolate_account` — attempt to suspend or disable the identity in the configured IdP (Okta or MS Graph). Requires admin creds.
2. `reset_password` — reset password via IdP API or simulate if not configured.
3. `enforce_mfa` — re-register or force MFA where supported.
4. `block_domain` — add domains found in IOCs to an email/web gateway or blocklist (simulated by default).
5. `quarantine_emails` — notify mail system to quarantine messages related to the incident (simulated by default).

Notes:
- All steps are safe-simulated when integration env vars are not present. For production, ensure each action is idempotent and has a clear rollback.

## Audit and post-incident

- Audit entries are written by `audit.py` to `logs/playbook.log` as newline-delimited JSON. Each entry contains `timestamp`, `account`, `proposed_actions`, `approved`, `outcome`, and `results` (when executed).
- If `AUDIT_HMAC_SECRET` is set, entries include `_hmac` for verification.
- If `AUDIT_SERVICE_URL` is set, audit entries are POSTed to that service as a backup.

Post-incident tasks:
1. Review `logs/playbook.log` and any remote audit collector records.
2. Validate actions taken in IdP and mail gateway — confirm account suspension, password reset, and quarantine status.
3. Create a ticket in your incident tracking system summarizing actions and attach audit logs.
4. If containment was applied in error, follow the rollback procedure below.

## Rollback procedure (if containment was applied incorrectly)

1. Re-enable the account in IdP (reverse `isolate_account`) and restore prior state as appropriate.
2. Revoke or reissue credentials if necessary.
3. Restore mailflow or unblock domains.
4. Record rollback steps in the incident ticket and update audit logs.

## Alerts & monitoring

- Monitor `logs/playbook.log` for new entries. Use `tail -f` or configure centralized log forwarding.
- Configure alerting on unusual rates of playbook runs or repeated denied approvals.

## Troubleshooting

- Playbook times out waiting for webhook approval: verify `APPROVAL_STATUS_URL` is reachable from the host and that the approval server updated the request status.
- Audit writes fail: check filesystem permissions for `logs/` and environment settings for `AUDIT_SERVICE_URL`.
- Integration calls failing: verify API keys and account permissions for Okta, Microsoft Graph, VirusTotal, and AbuseIPDB.

## Contact & escalation

- Primary responder: On-call security analyst
- Escalation: Security team lead, Identity team, Email operations

## Appendix: Useful commands

- Run tests:
```
python -m unittest discover -v
```
- Lint and format:
```
black .
flake8
```

---

This runbook is a living document — review and adapt to your organization's policy before using in production.
