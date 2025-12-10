SOAR Phishing Incident Response Playbook Flowchart
==================================================

This folder contains the visual representation of the automated SOAR workflow.

Workflow Steps (Sequential):

1. Phishing Alert Triggered
   - Entry point: email detected as potential phishing

2. Extract IOCs (Indicators of Compromise)
   - Extract: sender email, URLs, file hashes, IP addresses
   - Tool: extract_iocs.py

3. Threat Intelligence Enrichment
   - Lookup extracted IOCs against TI feeds (VirusTotal, AbuseIPDB, MS Defender)
   - Annotate IOCs with reputation, threat scores, malware families
   - Tool: enrich_iocs.py

4. Risk Score Calculation
   - Compute a 0-100 risk score based on IOC count and enrichment data
   - Scoring rules: malicious URLs (+15), suspicious hashes (+20), suspicious senders (+10)
   - Tool: risk_score.py

5. Risk Decision (Risk >= 80?)
   - If YES: proceed to Automated Containment
   - If NO: proceed to Analyst Review (manual investigation)

6a. Automated Containment (High Risk)
   - Disable Account: disable the victim's account in identity provider
   - Reset Password: force a password reset
   - Enforce MFA: enable or require MFA on the account
   - Incident Logging: log all containment actions
   - Generate Report: create incident response report
   - End: playbook complete

6b. Analyst Review (Low Risk)
   - Route to security analyst for manual assessment
   - Analyst may escalate if additional context warrants containment

Tools & Modules:
- extract_iocs.py: IOC extraction
- enrich_iocs.py: Threat intelligence enrichment
- risk_score.py: Risk scoring
- containment.py: Automated containment orchestration
- playbook_demo.py: End-to-end orchestrator

For a visual diagram (Mermaid format), see SOAR_Playbook_Flowchart.md.
For PowerPoint slides or PNG screenshots, add SOAR_Playbook_Flowchart.pptx or SOAR_Playbook_Flowchart.png here.
