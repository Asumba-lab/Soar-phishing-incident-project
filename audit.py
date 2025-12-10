"""Audit logging utilities.

Provides a centralized audit logger with rotation, optional HMAC signing
for integrity, and optional forwarding to an external audit service.

Environment variables:
- AUDIT_LOG_PATH: path to the audit logfile (defaults to ./logs/playbook.log)
- AUDIT_LOG_MAX_BYTES: rotation size in bytes (default 5MB)
- AUDIT_LOG_BACKUP_COUNT: number of rotated files to keep (default 3)
- AUDIT_HMAC_SECRET: if set, signs audit payloads (HMAC-SHA256)
- AUDIT_SERVICE_URL: if set, POSTs audit entries to this URL
"""
from __future__ import annotations

import os
import json
import hmac
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
import requests

_logger: logging.Logger | None = None


def _ensure_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    path = os.environ.get("AUDIT_LOG_PATH", os.path.join(logs_dir, "playbook.log"))
    max_bytes = int(os.environ.get("AUDIT_LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup = int(os.environ.get("AUDIT_LOG_BACKUP_COUNT", "3"))

    logger = logging.getLogger("soar_audit")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backup)
        # Simple formatter that writes the message as-is (we will pass JSON strings)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        # Attempt to secure file permissions where possible
        try:
            os.chmod(path, 0o600)
        except Exception:
            # Windows and some filesystems may not support chmod; ignore
            pass

    _logger = logger
    return _logger


def _sign_payload(payload: str) -> str | None:
    secret = os.environ.get("AUDIT_HMAC_SECRET")
    if not secret:
        return None
    sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return sig


def log_audit(entry: Dict[str, Any]) -> None:
    """Append an audit entry.

    The entry will be augmented with a timestamp if missing, then written
    as a single-line JSON string to the rotating audit log. If configured,
    a signature will be attached under the `_hmac` key and the entry will
    be POSTed to `AUDIT_SERVICE_URL`.
    """
    logger = _ensure_logger()

    if "timestamp" not in entry:
        from datetime import datetime

        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

    payload = json.dumps(entry, ensure_ascii=False)
    sig = _sign_payload(payload)
    if sig:
        try:
            # Attach signature but keep original payload unchanged for local write
            signed = dict(entry)
            signed["_hmac"] = sig
            payload_to_write = json.dumps(signed, ensure_ascii=False)
        except Exception:
            payload_to_write = payload
    else:
        payload_to_write = payload

    logger.info(payload_to_write)

    # Optionally forward to external audit collector
    svc = os.environ.get("AUDIT_SERVICE_URL")
    if svc:
        headers = {"Content-Type": "application/json"}
        if sig:
            headers["X-Audit-Signature"] = sig
        try:
            requests.post(svc, data=payload_to_write.encode("utf-8"), headers=headers, timeout=5)
        except Exception:
            # Do not raise on remote audit failures; the local log remains the source of truth
            logging.getLogger(__name__).exception("Failed to forward audit entry to %s", svc)


__all__ = ["log_audit"]
