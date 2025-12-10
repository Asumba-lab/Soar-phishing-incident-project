"""Simple approval webhook server for demo/testing.

Endpoints:
- POST /request  -> create approval request, returns {"id": <id>}
- GET /status/<id> -> return {"id": id, "status": "pending"|"approved"|"denied"}
- POST /callback/<id> -> accept {"approved": true|false, "approver": "name"}

This is intentionally lightweight and for demo/testing only.
"""
from flask import Flask, request, jsonify
import uuid
import threading
import os

app = Flask(__name__)

# In-memory store; for demo we also persist requests/results to logs/ files
_requests = {}


def _ensure_logs():
    d = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(d, exist_ok=True)
    return d


@app.route("/request", methods=["POST"])
def create_request():
    body = request.get_json(force=True)
    req_id = str(uuid.uuid4())
    _requests[req_id] = {"status": "pending", "request": body}

    # persist a record for operators to inspect
    d = _ensure_logs()
    try:
        with open(os.path.join(d, "approval_requests.jsonl"), "a", encoding="utf-8") as fh:
            import json

            fh.write(json.dumps({"id": req_id, "request": body}) + "\n")
    except Exception:
        pass

    # Simulate sending a notification (in real use send email/webhook)
    print(f"Approval request created: {req_id}")
    return jsonify({"id": req_id}), 201


@app.route("/status/<req_id>", methods=["GET"])
def status(req_id):
    r = _requests.get(req_id)
    if not r:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"id": req_id, "status": r["status"]})


@app.route("/callback/<req_id>", methods=["POST"])
def callback(req_id):
    r = _requests.get(req_id)
    if not r:
        return jsonify({"error": "not_found"}), 404
    body = request.get_json(force=True)
    approved = bool(body.get("approved"))
    r["status"] = "approved" if approved else "denied"
    r["approver"] = body.get("approver")

    d = _ensure_logs()
    try:
        with open(os.path.join(d, "approval_results.jsonl"), "a", encoding="utf-8") as fh:
            import json

            fh.write(json.dumps({"id": req_id, "approved": approved, "approver": r.get("approver")}) + "\n")
    except Exception:
        pass

    return jsonify({"id": req_id, "status": r["status"]})


def run_server(port: int = 5000):
    # Run Flask development server; for production use a WSGI server
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
