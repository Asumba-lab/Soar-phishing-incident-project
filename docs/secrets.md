# Secrets and CI Secret Setup

This document explains how to configure API keys and secrets for running real integrations in the demo, and how to add them to GitHub Actions safely.

## Environment variables (local)

Place sensitive values in environment variables or a secure vault. For local testing you can use a `.env` file (do not commit it).

Supported variables:

- `VIRUSTOTAL_API_KEY` — VirusTotal API v3 key
- `ABUSEIPDB_API_KEY` — AbuseIPDB API key
- `MS_DEFENDER_KEY` — Microsoft Defender TI (demo stub)
- `OKTA_API_TOKEN` — Okta API token
- `OKTA_DOMAIN` — Okta domain (e.g., `dev-123456.okta.com`)
- `MS_GRAPH_TOKEN` — Microsoft Graph OAuth token
- `REQUIRE_APPROVAL` — `true`/`false` (if true, supervisor approval is required before containment)
- `APPROVAL_MODE` — `cli` or `email` (CLI prompt or email-style stub)

## Example `.env.template`

```
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
MS_DEFENDER_KEY=
OKTA_API_TOKEN=
OKTA_DOMAIN=
MS_GRAPH_TOKEN=
REQUIRE_APPROVAL=false
APPROVAL_MODE=cli
```

Copy to `.env` and fill the values when running locally. Never commit `.env` to source control.

## GitHub Actions: adding secrets

1. Go to your repository on GitHub → Settings → Secrets and variables → Actions → New repository secret.
2. Add the secret names exactly as above (e.g., `VIRUSTOTAL_API_KEY`).
3. In your workflow, reference them as `secrets.VIRUSTOTAL_API_KEY`.

Example (partial step in `.github/workflows/ci.yml`):

```yaml
- name: Run tests (with secrets)
  env:
    VIRUSTOTAL_API_KEY: ${{ secrets.VIRUSTOTAL_API_KEY }}
    ABUSEIPDB_API_KEY: ${{ secrets.ABUSEIPDB_API_KEY }}
    OKTA_API_TOKEN: ${{ secrets.OKTA_API_TOKEN }}
    OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
  run: |
    python -m unittest discover -v
```

Note: For demos or CI runs, prefer storing secrets in GitHub Secrets and keep read access minimal. Avoid exposing secrets in logs.
