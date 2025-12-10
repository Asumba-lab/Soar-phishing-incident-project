SOAR Phishing Incident Response - Screenshot Documentation
==========================================================

This folder contains screenshots and visual artifacts from running the SOAR playbook demo.

SCREENSHOTS TO CAPTURE & INCLUDE:

1. terminal_execution.png
   Description: Full terminal output of running playbook_demo.py
   Expected Output:
   - IOC extraction results (emails, URLs, hashes)
   - Enrichment data with reputation scores
   - Risk score calculation (95 in sample)
   - Containment actions executed (isolate, reset_password, enforce_mfa, etc.)

2. ioc_extraction_output.png
   Description: JSON output from extract_iocs module
   Expected Output:
   {
     "emails": ["attacker@example.com", "victim_user@example.com"],
     "urls": ["https://malicious.example.com/invoice.pdf"],
     "ips": [],
     "hashes": ["d41d8cd98f00b204e9800998ecf8427e"]
   }

3. enrichment_output.png
   Description: Enriched IOCs with threat intelligence reputation data
   Expected Output:
   {
     "emails": {
       "attacker@example.com": {"reputation": "suspicious", "owner": "example.com"}
     },
     "urls": {
       "https://malicious.example.com/invoice.pdf": {"reputation": "malicious"}
     },
     "ips": {},
     "hashes": {...}
   }

4. risk_score_output.png
   Description: Risk score calculation step
   Expected Output:
   Risk score: 95

5. auto_containment_output.png
   Description: Automated containment actions executed
   Expected Output:
   {
     "isolate": {"account": "victim_user@example.com", "action": "isolated"},
     "reset_password": {"account": "victim_user@example.com", "action": "password_reset_simulated"},
     "enforce_mfa": {"account": "victim_user@example.com", "action": "enforce_mfa_simulated"},
     "blocked_domains": {"malicious.example.com": {"action": "blocked_simulated"}},
     "quarantine": {"quarantined": [...], "action": "quarantine_simulated"}
   }

ADDITIONAL SCREENSHOTS (OPTIONAL):

6. test_execution.png
   Description: Unit and integration test results
   Command: python -m unittest tests/test_playbook.py -v
   Expected: All tests pass with 'OK'

7. mocked_integration_tests.png
   Description: Mocked integration test results
   Command: python -m unittest tests/test_integrations_mocked.py -v
   Expected: Test cases for VirusTotal/AbuseIPDB and Okta flows

8. code_quality_check.png
   Description: Black and flake8 code quality validation
   Commands:
   - black --check .
   - flake8 --max-line-length=88

9. docker_build_and_run.png
   Description: Docker image build and container execution
   Commands:
   - docker build -t soar-phish-demo:latest .
   - docker run --rm soar-phish-demo:latest

10. github_actions_ci.png
    Description: GitHub Actions CI workflow execution
    Location: .github/workflows/ci.yml
    Shows: linting, formatting, and test execution results

11. playbook_output_json.png
    Description: Generated playbook_output.json artifact
    File: playbook_output.json
    Contains: Full IOC extraction, enrichment, risk score, and containment data

INSTRUCTIONS FOR CAPTURING SCREENSHOTS:

For Terminal Output (Windows PowerShell):
1. Run: python .\playbook_demo.py
2. Use Windows Snipping Tool or PrintScreen
3. Save as terminal_execution.png

For VS Code Integration Tests:
1. Open integrated terminal in VS Code
2. Run: python -m unittest tests/test_playbook.py -v
3. Capture output showing test results

For JSON Artifacts:
1. Open playbook_output.json in VS Code
2. Use color highlighting to show JSON structure
3. Capture as json_artifact.png

For Flowchart:
1. Reference flowchart/SOAR_Playbook_Flowchart.md
2. Export Mermaid diagram to PNG if available
3. Save as flowchart_screenshot.png
