"""Page Object for the document-capture step of the verification flow.

In production this step would drive a real camera widget; for
deterministic, CI-friendly automation the mock UI exposes an equivalent
file input, so the flow under test (capture -> submit -> processed) is
identical to the real one.

TODO (candidate): implement the methods below using the locators already
defined and the `_open` / `_find` / `_click` / `_text_of` helpers inherited
from `BasePage` (see `base_page.py`). The page served at
`GET /verify/{session_id}` (see `mock_server/app.py`) exposes:
  - a span #session-id showing the current session id
  - a file input #document-input
  - a button #submit-document that uploads the file and navigates to the
    result page
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from selenium.webdriver.common.by import By

from .base_page import BasePage


class UploadDocumentPage(BasePage):
    _FILE_INPUT = (By.ID, "document-input")
    _SUBMIT_BUTTON = (By.ID, "submit-document")
    _SESSION_LABEL = (By.ID, "session-id")

    def open(self, session_id: str) -> "UploadDocumentPage":
        """Navigate to the capture page for the given session id."""
        self._open(f"/verify/{session_id}")
        self._find(self._SUBMIT_BUTTON)  # page is ready once the CTA is rendered
        return self

    def displayed_session_id(self) -> str:
        """Return the session id shown on the page."""
        return self._text_of(self._SESSION_LABEL)

    def capture_document(self, file_path: Union[str, Path]) -> "UploadDocumentPage":
        """Simulate the camera capture by attaching a local file."""
        # File inputs need an absolute path; `presence` (not visibility) is
        # used because real capture widgets often hide the native input.
        self._find(self._FILE_INPUT).send_keys(str(Path(file_path).resolve()))
        return self

    def submit(self) -> "UploadDocumentPage":
        """Submit the captured document."""
        self._click(self._SUBMIT_BUTTON)
        return self
