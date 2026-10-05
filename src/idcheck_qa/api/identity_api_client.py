"""Domain-specific client for the Identity Verification API.

Public methods should speak the language of the business ("create a
session", "submit a captured document", "get verification status")
instead of raw HTTP verbs/paths, so calling code and tests read like a
specification of the product, not a list of curl commands.

TODO (candidate): implement the three methods below using `self.get` /
`self.post` from `BaseAPIClient` (see `base_client.py`) against the mock
backend in `mock_server/app.py`:

- POST /api/sessions                          -> {"session_id": ..., "status": "PENDING"}
- POST /api/sessions/{session_id}/document     -> multipart upload, field name "document"
                                                   -> {"session_id": ..., "status": ..., "reason": ...}
- GET  /api/sessions/{session_id}              -> {"session_id": ..., "status": ..., "reason": ...}

Map each JSON response into the typed models in `models.py`
(`VerificationSession.from_dict` / `VerificationStatus.from_dict`) instead
of returning raw dicts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from .base_client import BaseAPIClient
from .models import VerificationSession, VerificationStatus


class IdentityVerificationClient(BaseAPIClient):
    """Client for the `/api/sessions` identity-check endpoints."""

    SESSIONS_PATH = "/api/sessions"
    DOCUMENT_FIELD = "document"

    # --- endpoint paths (public so negative tests can reuse them with the
    # raw transport helpers instead of re-typing URLs) ---------------------
    def session_path(self, session_id: str) -> str:
        return f"{self.SESSIONS_PATH}/{session_id}"

    def document_path(self, session_id: str) -> str:
        return f"{self.session_path(session_id)}/document"

    # --- domain operations ----------------------------------------------
    def create_session(self, applicant_ref: str = "candidate-test") -> VerificationSession:
        """Create a new verification session and return it as a `VerificationSession`."""
        response = self.post(self.SESSIONS_PATH, json={"applicant_ref": applicant_ref})
        return VerificationSession.from_dict(response.json())

    def submit_document(
        self, session_id: str, document_path: Union[str, Path]
    ) -> VerificationStatus:
        """Submit a captured ID document for a session and return the resulting status.

        `document_path` is a local file path; simulate the camera capture by
        uploading it as multipart/form-data under the field name "document".
        """
        path = Path(document_path)
        # Only the filename is sent alongside the bytes -- never log the
        # document content: against a real KYC API it is personal data.
        with path.open("rb") as document:
            response = self.post(
                self.document_path(session_id),
                files={self.DOCUMENT_FIELD: (path.name, document, "image/jpeg")},
            )
        return VerificationStatus.from_dict(response.json())

    def get_status(self, session_id: str) -> VerificationStatus:
        """Fetch the current verification status for a session."""
        response = self.get(self.session_path(session_id))
        return VerificationStatus.from_dict(response.json())
