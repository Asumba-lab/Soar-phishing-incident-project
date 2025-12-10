% SOAR Phishing Incident Response — 5-slide Summary

---

# Slide 1 — Overview

- Purpose: Demonstrate an auditable SOAR playbook for phishing incidents.
- Flow: IOC extraction → Enrichment → Risk scoring → Approval → Containment.
- Audience: security engineers, SOC operators, and evaluators.

Notes: Use this slide to set the scope and emphasize safety-by-default.

---

# Slide 2 — Architecture & Data Flow

- Inputs: Email/message, user reports, external TI (VirusTotal/AbuseIPDB).
- Components:
  - `extract_iocs.py` (parses IOCs)
  - `enrich_iocs.py` (TI enrichment)
  - `risk_score.py` (heuristics)
  - `approval.py` + `approval_server.py` (human-in-the-loop)
  - `containment.py` & `isolate_account.py` (actions)
  - `audit.py` (rotating JSON audit logs, optional HMAC + forwarding)

Notes: Show arrows from inputs → extract → enrich → score → approval → containment → audit.

---

# Slide 3 — Approval & Audit

- Approval modes: `cli`, `email` (simulated), `webhook` (recommended for automation).
- Webhook flow: playbook POSTs request → approver calls callback → playbook polls and proceeds.
- Audit: newline-delimited JSON in `logs/playbook.log`; supports rotation and HMAC via `AUDIT_HMAC_SECRET`.

Notes: Stress the importance of HMAC and forwarding to a centralized collector for tamper detection.

---

# Slide 4 — Containment Actions & Safety

- Actions (idempotent via API where possible):
  - Suspend/disable account
  - Reset password
  - Enforce MFA
  - Block malicious domains
  - Quarantine emails
- Safety: simulated fallbacks when integrations are not configured; require `REQUIRE_APPROVAL` for destructive runs.

Notes: Outline rollback steps and require multi-person approval for production.

---

# Slide 5 — Next Steps & Operational Guidance

- Short-term: add vcrpy fixtures, add persistent approval store, add SIEM integration for audit logs.
- Long-term: production-grade approval UI, RBAC, ticketing integration, hardened container orchestration.
- Operations: runbook (see `docs/runbook.md`), monitor `logs/`, rotate `AUDIT_HMAC_SECRET`.

Notes: Provide contact points and recommended SLAs for approvals.
