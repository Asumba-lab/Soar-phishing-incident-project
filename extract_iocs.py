"""IOC extraction utilities for the SOAR phishing demo.
Provides simple regex-based extraction for emails, URLs, IPs and hashes.
"""

import re
from typing import Dict, List

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
URL_RE = re.compile(r"https?://[\w\.-/\?&=%#:~,+-]+")
IP_RE = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")


def extract_iocs(text: str) -> Dict[str, List[str]]:
    """Return a dictionary of extracted IOCs from text."""
    emails = sorted(set(EMAIL_RE.findall(text)))
    urls = sorted(set(URL_RE.findall(text)))
    ips = sorted(set(IP_RE.findall(text)))
    hashes = sorted(set(MD5_RE.findall(text)))
    return {"emails": emails, "urls": urls, "ips": ips, "hashes": hashes}


if __name__ == "__main__":
    import sys

    sample = """
    From: attacker@example.com
    Subject: Important update
    Hi,
    Please review: https://malicious.example.com/login. Contact admin@victim.local.
    File hash: d41d8cd98f00b204e9800998ecf8427e
    """
    text = sys.stdin.read() if not sys.stdin.isatty() else sample
    iocs = extract_iocs(text)
    import json

    print(json.dumps(iocs, indent=2))
