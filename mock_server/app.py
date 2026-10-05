"""Minimal, self-contained mock of an identity-verification backend + UI.

This is a *test double*, not production code: it exists purely so the
sample API/Selenium suite has something deterministic and fully offline
to exercise. No real camera, document storage, or biometric checks
happen here -- the outcome is decided from the uploaded filename so both
the "approved" and "rejected" branches of the flow are easy to test,
without needing anything resembling real personal/document data.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

_SESSIONS: Dict[str, Dict[str, Any]] = {}

_UPLOAD_PAGE = """
<!doctype html>
<html>
<body>
  <h1>Identity Verification</h1>
  <p>Session: <span id="session-id">{{ session_id }}</span></p>
  <input type="file" id="document-input" />
  <button id="submit-document" type="button" onclick="submitDoc()">Submit capture</button>
  <script>
    function submitDoc() {
      const input = document.getElementById('document-input');
      const formData = new FormData();
      formData.append('document', input.files[0]);
      fetch('/api/sessions/{{ session_id }}/document', { method: 'POST', body: formData })
        .then(() => { window.location.href = '/result/{{ session_id }}'; });
    }
  </script>
</body>
</html>
"""

_RESULT_PAGE = """
<!doctype html>
<html>
<body>
  <h1>Verification Result</h1>
  <p>Status: <span id="verification-status">{{ status }}</span></p>
</body>
</html>
"""


@app.post("/api/sessions")
def create_session():
    session_id = uuid.uuid4().hex[:12]
    _SESSIONS[session_id] = {"status": "PENDING", "reason": None}
    return jsonify({"session_id": session_id, "status": "PENDING"}), 201


@app.post("/api/sessions/<session_id>/document")
def submit_document(session_id: str):
    session = _SESSIONS.get(session_id)
    if session is None:
        return jsonify({"error": "session_not_found"}), 404

    uploaded = request.files.get("document")
    filename = (uploaded.filename or "").lower() if uploaded else ""

    if "invalid" in filename:
        session["status"] = "REJECTED"
        session["reason"] = "document_unreadable"
    else:
        session["status"] = "VERIFIED"
        session["reason"] = None

    return jsonify({"session_id": session_id, **session})


@app.get("/api/sessions/<session_id>")
def get_status(session_id: str):
    session = _SESSIONS.get(session_id)
    if session is None:
        return jsonify({"error": "session_not_found"}), 404
    return jsonify({"session_id": session_id, **session})


@app.get("/verify/<session_id>")
def verify_page(session_id: str):
    return render_template_string(_UPLOAD_PAGE, session_id=session_id)


@app.get("/result/<session_id>")
def result_page(session_id: str):
    session = _SESSIONS.get(session_id, {"status": "UNKNOWN"})
    return render_template_string(_RESULT_PAGE, status=session["status"])


@app.get("/")
def health():
    return jsonify({"service": "idcheck-mock", "status": "ok"})


def reset_state() -> None:
    """Test helper: clears in-memory sessions between test functions."""
    _SESSIONS.clear()


if __name__ == "__main__":
    # Manual/exploratory testing needs the app running as a standalone
    # process; a pytest suite can instead boot it in-process via a fixture.
    # Defaults match .env.example's IDCHECK_BASE_URL.
    port = int(os.getenv("IDCHECK_MOCK_PORT", "5005"))
    app.run(host="127.0.0.1", port=port)
